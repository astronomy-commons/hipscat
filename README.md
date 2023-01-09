# HiPSCat

**Hierarchical Progressive Survey Catalog**

A HiPSCat catalog is a partitioning of objects on a sphere. Its purpose is for storing data from large astronomy surveys, but could probably be used for other use cases where you have large data with some spherical properties.

## Partitioning Scheme

We use healpix (Hierarchical Equal Area isoLatitude Pixelization [[more](https://healpix.jpl.nasa.gov/)]) for the spherical pixelation, and adaptively size the partitions based on the number of objects.

In areas of the sky with more objects, we use smaller pixels, so that all the resulting pixels should contain similar counts of objects (within an order of magnitude).

## File structure

The catalog reader expects to find files according to the following partitioned structure:

```
__ /path/to/catalogs/<catalog_name>/
  |__ catalog_info.json
  |__ partition_info.csv
  |__ Norder1/
  |  |__ Npix0/catalog.parquet
  |  |__ Npix1/catalog.parquet
  |__ NorderJ/
     |__ NpixK/catalog.parquet
     |__ NpixM/catalog.parquet
```

## Installation


```bash
$ conda create -n hipscatenv python=3.8
$ source activate hipscatenv
$ cd ~/git
$ git clone https://github.com/astronomy-commons/hipscat
$ cd hipscat
$ source setup.bash
$ pip install -e .
```