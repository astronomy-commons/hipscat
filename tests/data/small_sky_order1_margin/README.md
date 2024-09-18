# Catalog description

This catalog exists as an margin cache of the small_sky_order1 table,
allowing spatial operations to be performed efficiently and accurately.

This catalog was generated using the following snippet:

```
from _import.margin_cache.margin_cache_arguments import MarginCacheArguments
from _import.margin_cache import generate_margin_cache

margin_args = MarginCacheArguments(
    margin_threshold=7200,
    input_catalog_path="data/small_sky_order1",
    output_path="data/",
    output_artifact_name="small_sky_order1_margin"
)


if __name__ == "__main__":
    generate_margin_cache(margin_args, client)
```

NB: 

- The setting `margin_threshold` at 7200 arcseconds (2 degrees) is much higher than
  a usual margin cache would be generated at, but is used because the small sky test
  dataset is sparse.
- The `small_sky_order1` catalog only contains points in Norder1, Npix=[44, 45, 46, 47], but the margin catalog also contains points in Norder0, Npix=4 due to negative pixel margins.
