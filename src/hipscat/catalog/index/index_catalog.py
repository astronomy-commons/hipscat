from typing import List

import numpy as np
import pyarrow.compute as pc
import pyarrow.dataset as pds
from typing_extensions import TypeAlias

from hipscat.catalog.dataset import Dataset
from hipscat.catalog.index import IndexCatalogInfo
from hipscat.io import paths
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.healpix_pixel_function import get_pixel_argsort


class IndexCatalog(Dataset):
    """An index into HiPSCat Catalog for enabling fast lookups on non-spatial values.

    Note that this is not a true "HiPScat Catalog", as it is not partitioned spatially.
    """

    CatalogInfoClass: TypeAlias = IndexCatalogInfo
    catalog_info: CatalogInfoClass

    def loc_partitions(self, ids) -> List[HealpixPixel]:
        """Find the set of partitions in the primary catalog for the
        ids provided.

        Args:
            ids: the values of the indexing column (e.g. 87,543)
        Returns:
            partitions of leaf parquet files in the primary catalog
            that may contain rows for the id values
        """
        metadata_file = paths.get_parquet_metadata_pointer(self.catalog_base_dir)
        dataset = pds.parquet_dataset(metadata_file)

        filtered = dataset.filter(pc.field(self.catalog_info.indexing_column).isin(ids)).to_table()
        python_friendly = filtered.group_by(["Norder", "Npix"]).aggregate([]).to_pandas()

        loc_partitions = [
            HealpixPixel(order, pixel)
            for order, pixel in zip(
                python_friendly["Norder"],
                python_friendly["Npix"],
            )
        ]
        argsort = get_pixel_argsort(loc_partitions)
        loc_partitions = np.array(loc_partitions)[argsort]

        return loc_partitions
