# Catalog description

This catalog has the same data points as other small sky catalogs,
but is coerced to spreading these data points over partitions at order 1, instead
of order 0.

This means there are 4 leaf partition files, instead of just 1, and so can
be useful for confirming reads/writes over multiple leaf partition files.

This catalog was generated with the following snippet:

```
import hats_import.pipeline as runner
from hats_import.catalog.arguments import ImportArguments

def create_order1():
    args = ImportArguments(
        input_path="tests/_import/data/small_sky",
        output_path="tests/data",
        input_format="csv",
        output_artifact_name="small_sky_order1",
        constant_healpix_order=1,
    )
    runner.pipeline(args)

if __name__ == "__main__":
    create_index()
```

NB: Setting `constant_healpix_order` coerces the import pipeline to create
leaf partitions at order 1.