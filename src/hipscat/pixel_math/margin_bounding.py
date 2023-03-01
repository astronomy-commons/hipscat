"""Utilities to build bounding boxes around healpixels that include a neighor margin."""

import healpy as hp
import numpy as np

from astropy.coordinates import SkyCoord
from regions import PixCoord, PolygonSkyRegion, PolygonPixelRegion
import astropy.wcs as wcs

def get_margin_scale(pixel_order, margin_threshold=0.1):
    """Get the scale value need to expand the pixel bounding box to include the `margin_threshold`.

    Args:
        pixel_order (int): the order of the pixel to which we're calculating the margin region for.
        margin_threshold (float): the size of the border region in degrees.
    Returns:
        a float representing the scale factor.
    """
    if margin_threshold <= 0.:
        raise ValueError("margin_threshold must be greater than 0.")
    
    resolution = hp.nside2resol(2**pixel_order, arcmin=True) / 60.
    resolution_and_thresh = resolution + (margin_threshold)
    margin_area = resolution_and_thresh ** 2
    pixel_area = hp.pixelfunc.nside2pixarea(2**pixel_order, degrees=True)
    scale = margin_area / pixel_area
    return scale

def get_margin_bounds_and_wcs(pixel_order, pix, scale, step=10):
    """Get the astropy `regions.PolygonPixelRegion` and `astropy.wcs` objects for a given margin bounding box scale.
    
    Args:
        pixel_order (int): the order of the pixel to which we're calculating the margin region for.
        pix (int): the healpixel which we're calculating the margin region for.
        scale (float): the scale factor to apply to the given healpixel.
        step (int): the amount of samples of one side of the given healpixel's boundaries.
            total samples taken = 4 * step.
    Returns:
        polygons (list of tuples): a list of obj:`regions.PolygonPixelRegion` and obj:`wcs.WCS` tuples, covering the full area of the given healpixels scaled up area.
    """
    
    pixel_boundaries = hp.vec2dir(hp.boundaries(2**pixel_order, pix, step=step, nest=True), lonlat=True)

    # find the translation values to keep the bounding box
    # centered around the orignal healpixel.
    n_samples = len(pixel_boundaries[0])
    centroid_lon = np.sum(pixel_boundaries[0]) / n_samples
    centroid_lat = np.sum(pixel_boundaries[1]) / n_samples
    translate_lon = centroid_lon - (centroid_lon * scale)
    translate_lat = centroid_lat - (centroid_lat * scale)

    affine_matrix = np.array([[scale, 0, translate_lon],
                              [0, scale, translate_lat],
                              [0,     0,             1]])

    # convert the orignal boundary coordinates into
    # a homogenous coordinate space (3-dim)
    homogeneous = np.ones((3, n_samples))
    homogeneous[0] = pixel_boundaries[0]
    homogeneous[1] = pixel_boundaries[1]

    transformed_bounding_box = np.matmul(affine_matrix, homogeneous)

    # if the transform places the declination of any points outside of
    # the range 90 > dec > -90, change it to a proper dec value.
    for i in range(len(transformed_bounding_box[1])):
        dec = transformed_bounding_box[1][i]
        if dec > 90.:
            transformed_bounding_box[1][i] = 90. - (dec - 90.)
        elif dec < -90.:
            transformed_bounding_box[1][i] = -90. - (dec + 90.)


    min_ra = np.min(transformed_bounding_box[0])
    max_ra = np.max(transformed_bounding_box[0])
    min_dec = np.min(transformed_bounding_box[1])
    max_dec = np.max(transformed_bounding_box[1])

    # one arcsecond
    pix_size = 0.0002777777778

    ra_naxis =int((max_ra - min_ra) / pix_size)
    dec_naxis = int((max_dec - min_dec) / pix_size)

    polygons = []
    # for k < 2, the size of the bounding boxes breaks the regions
    # code, so we subdivide the pixel into multiple parts with
    # independent wcs.
    if pixel_order < 2:
        for i in range(4):    
            j = i * step
            lon = list(transformed_bounding_box[0][j:j+step+1])
            lat = list(transformed_bounding_box[1][j:j+step+1])

            lon.append(centroid_lon)
            lat.append(centroid_lat)

            wcs_partial = wcs.WCS(naxis=2)
            wcs_partial.wcs.crpix = [1, 1]
            wcs_partial.wcs.crval = [lon[0], lat[0]]
            wcs_partial.wcs.cunit = ["deg", "deg"]
            wcs_partial.wcs.ctype = ["RA---TAN", "DEC--TAN"]
            wcs_partial.wcs.cdelt = [pix_size, pix_size]
            wcs_partial.array_shape = [int(ra_naxis/2), int(dec_naxis/2)]

            vertices = SkyCoord(lon, lat, unit='deg')
            sky_region = PolygonSkyRegion(vertices=vertices)
            polygons.append((sky_region.to_pixel(wcs_partial), wcs_partial))
    else:
        wcs_margin = wcs.WCS(naxis=2)
        wcs_margin.wcs.crpix = [1, 1]
        wcs_margin.wcs.crval = [min_ra, min_dec]
        wcs_margin.wcs.cunit = ["deg", "deg"]
        wcs_margin.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        wcs_margin.wcs.cdelt = [pix_size, pix_size]
        wcs_margin.array_shape = [ra_naxis, dec_naxis]

        vertices = SkyCoord(transformed_bounding_box[0], transformed_bounding_box[1], unit='deg')
        sky_region = PolygonSkyRegion(vertices=vertices)
        polygon_region = sky_region.to_pixel(wcs_margin)
        polygons = [(polygon_region, wcs_margin)]

    return polygons