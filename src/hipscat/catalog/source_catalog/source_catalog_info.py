"""Catalog Info for a HiPSCat Source (detection/timeseries) table"""

from dataclasses import dataclass

from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType


@dataclass
class SourceCatalogInfo(CatalogInfo):
    """Catalog Info for a HiPSCat Source (detection/timeseries) table.

    Includes some optional specification for timeseries-level columns.
    """

    primary_catalog: str = None
    """Object catalog reference"""

    mjd_column: str = ""
    """Column name for time of observation"""

    band_column: str = ""
    """Column name for photometric band"""

    mag_column: str = ""
    """Column name for magnitude measurement"""

    mag_err_column: str = ""
    """Column name for error in magnitude measurement"""

    DEFAULT_TYPE = CatalogType.SOURCE
    REQUIRED_TYPE = CatalogType.SOURCE

    ## NB: No additional required columns.
