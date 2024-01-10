# Catalog description

This catalog exists as an index of the SOURCE table, using the OBJECT ID
as the indexed column. This means you should be able to quickly find
partions of SOURCES for a given OBJECT ID.

This catalog was generated using the following snippet:

```
import hipscat_import.pipeline as runner
from hipscat_import.index.arguments import IndexArguments

def create_index():
    args = IndexArguments(
        input_catalog_path="./tests/hipscat_import/data/small_sky_source_catalog/",
        indexing_column="object_id",
        output_path="./tests/data/",
        output_artifact_name="small_sky_source_object_index",
        include_hipscat_index=False,
        compute_partition_size=200_000,
    )
    runner.pipeline(args)


if __name__ == "__main__":
    create_index()
```

NB: 

- Setting `compute_partition_size` to something less than `1_000_000` 
  coerces the import pipeline to create smaller result partitions, 
  and so we have three distinct index partitions.
- Setting `include_hipscat_index=False` keeps us from needing a row for every 
  source and lets the indexing pipeline create only one row per 
  unique objectId/Norder/Npix