HiPSCat Directory Scheme
===============================================================================

Partitioning Scheme
-------------------------------------------------------------------------------

We use healpix (`Hierarchical Equal Area isoLatitude Pixelization <https://healpix.jpl.nasa.gov/>`_)
for the spherical pixelation, and adaptively size the partitions based on the number of objects.

In areas of the sky with more objects, we use smaller pixels, so that all the 
resulting pixels should contain similar counts of objects (within an order of 
magnitude).

File structure
-------------------------------------------------------------------------------

The catalog reader expects to find files according to the following partitioned 
structure:

.. code-block:: 
        
    __ /path/to/catalogs/<catalog_name>/
       |__ catalog_info.json
       |__ partition_info.csv
       |__ Norder=1/
       |   |__ Dir=0/
       |       |__ Npix=0.parquet
       |       |__ Npix=1.parquet
       |__ Norder=J/
           |__ Dir=10000/
               |__ Npix=K.parquet
               |__ Npix=M.parquet