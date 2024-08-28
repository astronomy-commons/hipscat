from typing import List

import numpy as np
import pyarrow.compute as pc
import pyarrow.dataset as pds
from typing_extensions import TypeAlias

from hipscat.catalog.dataset import Dataset
from hipscat.catalog.index import IndexCatalogInfo
from hipscat.io import paths

# from hipscat.io.file_io.file_pointer import get_fs, strip_leading_slash_for_pyarrow
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.healpix_pixel_function import get_pixel_argsort


class IndexCatalog(Dataset):
    """An index into HiPSCat Catalog for enabling fast lookups on non-spatial values.

    Note that this is not a true "HiPScat Catalog", as it is not partitioned spatially.
    """

    CatalogInfoClass: TypeAlias = IndexCatalogInfo
    catalog_info: CatalogInfoClass

    def loc_partitions(self, ids) -> List[HealpixPixel]:
        """Find the set of partitions in the primary catalog for the ids provided.

        Args:
            ids: the values of the indexing column (e.g. 87,543)
        Returns:
            partitions of leaf parquet files in the primary catalog
            that may contain rows for the id values
        """
        metadata_file = paths.get_parquet_metadata_pointer(self.catalog_base_dir)
        # file_system, metadata_file = get_fs(file_pointer=metadata_file, storage_options=self.storage_options)

        # # pyarrow.dataset requires the pointer not lead with a slash
        # metadata_file = strip_leading_slash_for_pyarrow(metadata_file, file_system.protocol)

        dataset = pds.parquet_dataset(metadata_file, filesystem=metadata_file.fs)

        # There's a lot happening in a few pyarrow dataset methods:
        # We create a simple pyarrow expression that roughly corresponds to a SQL statement like
        #   WHERE id_column IN (<ids>)
        # We stay in pyarrow to group by Norder/Npix to aggregate the results unique values.
        # After that convert into pandas, as this handles the integer type conversions
        # (uint8 and uint64 aren't always friendly between pyarrow and the rest of python),
        # and offers easy iteration to create our HealpixPixel list.
        filtered = dataset.filter(pc.field(self.catalog_info.indexing_column).isin(ids)).to_table()
        unique_pixel_dataframe = filtered.group_by(["Norder", "Npix"]).aggregate([]).to_pandas()

        loc_partitions = [
            HealpixPixel(order, pixel)
            for order, pixel in zip(
                unique_pixel_dataframe["Norder"],
                unique_pixel_dataframe["Npix"],
            )
        ]
        # Put the partitions in stable order (by nested healpix ordering).
        argsort = get_pixel_argsort(loc_partitions)
        loc_partitions = np.array(loc_partitions)[argsort]

        return loc_partitions
