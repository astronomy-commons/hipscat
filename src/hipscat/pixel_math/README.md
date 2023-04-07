# Pixel Math Appendix
A reference document for the various utility functions of `hipscat/pixel_math`.

## Pixel Margins
The functions made to find the pixels that make up the border region of a given 
healpixel. Primarly used as a way to speed up the neighbor/margin caching code 
for [hipscat-import](https://github.com/astronomy-commons/hipscat-import/). Code 
originally created by Mario Juric for HIPS, found 
[here](https://github.com/mjuric/HIPS/blob/feature/multiprocess/hipscat/healpix.py).

### get_edge
Given a pixel pix at some order, return all
pixels order dk _higher_ than pix's order that line
pix's edge (or a corner).

pix: the pixel ID for which the margin is requested
dk: the requested order of edge pixel IDs, relative to order of pix
edge: which edge/corner to return (NE edge=0, E corner=1, SE edge = 2, ....)

#### Algorithm

If you look at how the NEST indexing scheme works, a pixel at some order is
subdivided into four subpixel at every subsequent order in such a way that the south
subpixel index equals `4*pix`, east is `4*pix+1`, west is `4*pix+2`, north is `4*pix+3`:

```
                4*pix+3
pix ->     4*pix+2    4*pix+1
                4*pix
```

Further subdivisions split up each of those sub pixels accordingly. For example,
the eastern subpixel (`4*pix+1`) gets divided up into four more:

```
S=4*(4*pix+1), E=4*(4*pix+1)+1, W=4*(4*pix+1)+2, N=4*(4*pix+1)+3

                                                            4*(4*pix+3)+3
                4*pix+3                             4*(4*pix+3)+2   4*(4*pix+3)+1
                                            4*(4*pix+2)+3   4*(4*pix+3)   4*(4*pix+1)+3
pix ===>  4*pix+2    4*pix+1  ===>  4*(4*pix+2)+2   4*(4*pix+2)+1   4*(4*pix+1)+2   4*(4*pix+1)+1
                                            4*(4*pix+2)    4*(4*pix)+3    4*(4*pix+1)
                4*pix                                4*(4*pix)+2   4*(4*pix)+1
                                                                4*(4*pix)
```
etcetera...

We can see that the edge indices follow a pattern. For example, after two
subdivisions the south-east edge would consist of pixels:
```
4*(4*pix), 4*(4*pix)+1
4*(4*pix+1), 4*(4*pix+1)+1
```
with the top coming from subdividing the southern, and bottom the eastern pixel.
and so on, recursively, for more subdivisions. Similar patterns are identifiable
with other edges.

This can be compactly written as:

```
4*(4*(4*pix + i) + j) + k ....
```

with i, j, k, ... being indices whose choice specifies which edge we get.
For example iterating through, i = {0, 1}, j = {0, 1}, k = {0, 1} generates 
indices for the 8 pixels of the south-east edge for 3 subdivisions. Similarly, 
for the north-west edge the index values would loop through {2, 3}, etc.

This can be expanded as:

```
4**dk*pix  +  4**(dk-1)*i + 4**(dk-2)*j + 4**(dk-3) * k + ...
```

where dk is the number of subdivisions. E.g., for dk=3, this would equal:

```
4**3*pix + 4**2*i + 4**1*j + k
```

When written with bit-shift operators, another interpretation becomes clearer:

```
pix << 6 + i << 4 + j << 2 + k
```

or if we look at the binary representation of the resulting number:

```
    [pix][ii][jj][kk]
```

Where ii, jj, kk are the bits of _each_ of the i,j,k indices. That is, to get the
list of subpixels on the edge, we bit-shift the base index pix by 2*dk to the left,
and fill in the rest with all possible combinations of ii, jj, kk indices. For example,
the northeast edge has index values {2, 3} = {0b10, 0b11}, so for (say) pix=8=0b1000, the
northeast edge indices after two subdivisions are equal to:

```
0b1000 10 10 = 138
0b1000 10 11 = 139
0b1000 11 10 = 148
0b1000 11 11 = 143
```

Note that for a given edge and dk, the suffix of each edge index does not depend on
the value of pix (pix is bit-shifted to the right and added). This means it can be
precomputed & stored for repeated reuse.

#### Implementation

The implementation is based on the binary digit interpretation above. For a requested
edge and dk subdivision level, we generate (and cache) the suffixes. Then, for a given
pixel pix, the edge pixels are readily computed by left-shifting pix by 2*dk places,
and summing (== or-ing) it with the suffix array.

### get_margin
Returns the list of indices of pixels of order (kk+dk) that
border the pixel pix of order kk.

#### Algorithm
Given a pixel pix, find all of its neighbors. Then find the
edge at level (kk+dk) for each of the neighbors.

This is relatively straightforward in the equatorial faces of the Healpix
sphere -- e.g., one takes the SW neighbor and requests its NE edge to get
the margin on that side of the pixel, then the E corner of the W neighbor,
etc...

This breaks down on pixels that are at the edge of polar faces. There,
the neighbor's sense of direction _rotates_ when switching from face to
face. For example at order=2, pixel 5 is bordered by pixel 26 to the
northeast (see the Fig3, bottom, https://healpix.jpl.nasa.gov/html/intronode4.htm).
But to pixel 5 that is the **northwest** edge (and not southwest, as you'd
expect; run `hp.get_all_neighbours(4, 26, nest=True)` and
`hp.get_all_neighbours(4, 5, nest=True)` to verify these claims).

This is because directions rotate 90deg clockwise when moving from one
polar face to another in easterly direction (e.g., from face 0 to face 1).
We have to identify when this happens, and change the edges we request
for such neighbors. Mathematically, this rotation is equal to adding +2
(modulo 8) to the requested edge in get_edge(). I.e., for the
pixel 5 example, rather than requesting SE=4 edge of pixel 26,
we request SE+2=6=NE edge (see the comments in the definition of _edge_vectors
near get_edge()).

This index shift generalizes to `2 * (neighbor_face - pix_face)` for the case
when _both_ faces are around the pole (either north or south). In the south,
the rotation is in the opposite direction (ccw) -- so the sign of the shift
changes. The generalized formula also handles the pixels whose one vertex
is the pole (where all three neighbors sharing that vertex are on different
faces).

#### Implementation
Pretty straightforward implementation of the algorithm above.

### pixel_is_polar
Because of the nature of spherical coordinate systems, hipscat runs into some tricky edge cases at the poles. to ensure we can appropriately handle those problems, we need to check if a pixel is one of the four 'polar pixels'.

#### Algorithm
In the ring id scheme for `healpix`, the first and last 4 pixels are the polar pixels. To determine whether a nest scheme pixel is at the poles, all we have to do is convert the pixel into the ring scheme and determine if it falls at the beginning or end of the range 0 -> npix. So, if in the ring scheme the pix is `<= 3`, or `>= npix - 4`, we can safely assume that it is a polar pixel.

### get_truncated_margin_pixels
For pixels that are at the poles, our margin bounding box isn't set up to handle the data that is on the other side of the hemisphere from the partition. So when we calculate the boundaries, we truncate declination values outside of the range -90 -> 90. However, we obviously still want to include neighbor margin data that is affected by this truncation, namely the 3 margin pixels that are also polar pixels.

#### Algorithm
We want to find the 3 pixels at the healpix order of our margins that are polar. This is all of the pixels around the given pole _except_ the one that is contained within our partition pixel. 

For the north pole, this is straightforwardly done by converting our partition pixel into the ring id scheme and returning the values between 0 and 3 that aren't equal to it.

For the south pole, we have to do a little more complicated math, due to the fact that the southern polar pixels aren't the same values at any healpix order. To find the at polar pixel at the `margin_order` that is contained by the partition pixel (and therefore to be excluded), we can take advantage of the fact that in the nest scheme the southern partition of a pixel is equal to `4 * pix` (see the algorithm section of `get_edge` above for more info), so to get the excluded southern pixel all we have to do is find the difference between `order` and `margin_order`, and multiply our `pix` value by `4 ** d_order`.

## Margin Bounding
After constraining our data points using the `get_margin` code in `pixel_margins`, we then move on to our more accurate bound checking by building bounding boxes that include a region approximately one `margin_threshold` wide around the original healpixel.

To get this bounding box, we
- find a `scale` factor to apply to the original healpixel boundaries that increases the resolution by one `margin_threshold`
- sample a set of points along the boundary of a healpixel
- apply an affine transformation to these points to center them on the original healpixel

resulting in a box that covers a border region of one `margin_threshold` around the original healpixel.

We then can input these points into an astropy `regions.PolygonPixelRegion` object that we can the use to quickly check different datapoints against, resulting in a set of data for the final `neighbors.parquet` file.

### get_margin_scale
Finds the scale factor that we want to use to scale up the healpixel bounds by to include the neighbor margin.

#### Algorithm
- get the resolution of our `pixel_order` (sqrt of the pixel area)
- add the `margin_threshold` to the resolution and square it.
- divide this new area against the original pixel area to find the scale factor.

### get_margin_bounds_and_wcs
Given a healpixel and a scale factor, generate a `regions.PolygonPixelRegion` polygon and an `astropy.wcs.WCS` object containing the points of the healpixel scaled around the centroid by a factor of `scale`. Used in conjunction with `get_margin_scale` to perform an affine transform on a set of coordinates sampled from the boundaries of a healpixel.

By returning it as a pixel region along with a wcs object, we can quickly check data points against our polygon.

In the case where `pixel_order` is less than 2, we divide the polygon into 4 or 16 different polygon regions (orders **0** and **1** respectively), each with their own `WCS` object. We do this because `PolygonPixelRegions` start to break down with large bounding boxes at the granular coordinate spaces that we're using.

#### Algorithm
- get a sample of the healpixel boundaries (4 * `step`)
- find the centroid of the boundary coordinates, apply the `scale` to it, and find the difference from the original to find the translation values.
    - this translation keeps the bounding box centered on the orignal healpixel, as an affine transform scales from the origin of the coordinate system.
- build the [affine transform](https://en.wikipedia.org/wiki/Affine_transformation#Image_transformation) matrix.
- convert the boundary coordinates into [homogeneous coordinates](https://en.wikipedia.org/wiki/Homogeneous_coordinates).
- apply the affine transform to the now homogeneous coordinates.
- build the polygon(s) and wcs object(s) for the now transformed points.

### check_margin_bounds
Given a set of ra and dec coordinates as well as a list of `regions.PolygonPixelRegion` and `astropy.wcs.WCS` tuples (see `get_margin_bounds_and_wcs` above), return a 1-dimmensional array of booleans on whether a given ra and dec coordinate pair are contained within any of the given bounding boxes.

#### Implementation
For ever entry into `poly_and_wcs`, we convert our set of coordinates into pixel values using the `astropy.wcs.utils.skycoord_to_pixel` function then use the built in `contains` function to return the list of bound checks.

### check_polar_margin_bounds
For healpixels that surround the poles, the affine transform math breaks down directly around the poles, making it much harder for us to properly check margin data on the opposite hemisphere to our pixel. To solve this problem, we can use the `get_truncated_pixels` to find out what margin data falls around the poles, and then manually check the angular distance between those points and the boundaries of the given partition pixel to find out if the data point falls within a `margin_threshold` distance. While this sort of N^2 calculation isn't practical or desired for the larger dataset, this edge case usually only affects a small amount of the total potential margin cache data for a given catalog.

#### Algorithm
- Find the ratio of the `margin_order` (i.e. the order that our margin pixels are at) to the `order` of the larger partition pixel so that we can find the approximate range of samples to take from the `hp.boundaries` of our healpixel, giving us a set of points that define the border of the pixel along the poles.
    - Even at very high `step` values, this generally doesn't return a large number of points to check against, since even having a small difference between `order` and `margin_order` leads to exponentially smaller values of this ratio.
    - Higher `step` values didn't meaningfully increase the accuracy for `margin_threshold` checks so the default is value 1000, but we've left `step` as variable so that should more granularity be needed a user can adjust this value.
- Make sure none of these `polar_boundaries` values fall outside of the range -90 -> 90 declination, as sometimes `hp.boundaries` can return values a few millionths lower or higher at highly granular `step` values.
- Get the angular distance of our `r_asc` and `dec` values and our boundary values.
- Return `True` for any coordinates that have a distance less than or equal to `margin_threshold`.

## HiPSCat ID

This index is defined as a 64-bit integer which has two parts:

* healpix pixel (at order 19)
* incrementing counter (within same healpix, for uniqueness)

Visually, in bits:

```
|------------------------------------------|-------------------|
|<-----    healpixel at order 19    ------>|<--   counter   -->|
```

This provides us with an increasing index, that will not overlap
between spatially partitioned data files.

### compute_hipscat_id

For a given list of coordinates, compute the HiPSCat ID s.t. coordinates in the
same order 19 pixel are appended with a counter to make a unique hipscat_id.

For the example, we'll work with the following simplified hex numbers to help 
illustrate: `[0xbeee, 0xbeef, 0xbeee, 0xfeed, 0xbeef]`

#### Counter construction

To construct our counters we sort the pixel numbers, call 
[numpy.unique](https://numpy.org/doc/stable/reference/generated/numpy.unique.html),
then do some silly arithmetic with the results.

The sorted representation of the above is `[beee, beee, beef, beef, feed]`. What 
we're looking for at this point is a counter that indicates if the value is being
repeated and how many times we've seen this value so far. e.g. `[0, 1, 0, 1, 0]`.

The `np.unique` call will yield three outputs:

* `unique_values` (ignored) `[beee, beef, feed]`
* `unique_indices` - the index of the *first* occurrence of each unique value.
    `[0, 2, 4]`
* `unique_inverse` - the indices of *all* occurrences of the unique values 
    (using indexes from that `unique_values`), used to reconstruct the 
    original array. `[0, 0, 1, 1, 2]`

By indexing into `unique_indexes` by the `unique_inverse`, we get an array with the 
index of the first time that healpix pixel was seen, which provides an step-like 
offset. e.g. `[0, 0, 2, 2, 4]`. This jumps up to the current index each time the
pixel changes. We subtract this from the actual index value (e.g. `[0, 1, 2, 3, 4]`)
to get the desired counter. e.g. 

```
[0, 1, 2, 3, 4]
-
[0, 0, 2, 2, 4]
=
[0, 1, 0, 1, 0]
```

#### Putting it together

After mapping our coordinates into order 19 healpix pixels, we bit-shift them to make room for our counters. Then we add the counters to the end.

e.g.

```
[     0xbeee,      0xbeee,      0xbeef,      0xbeef,      0xfeed]
           << shifted <<
[0x5F7700000, 0x5F7700000, 0x5F7780000, 0x5F7780000, 0x7F7680000]
+
[          0,           1,            0,          1,           0]
=
[0x5F7700000, 0x5F7700001, 0x5F7780000, 0x5F7780001, 0x7F7680000]
```

And finally, we unsort the array to get back the hipscat ids in the order the 
coordinates were provided.

`[0x5F7700000, 0x5F7780000, 0x5F7700001, 0x7F7680000, 0x5F7780001]`