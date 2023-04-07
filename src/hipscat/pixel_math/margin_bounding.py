"""Utilities to build bounding boxes around healpixels that include a neighor margin."""

import healpy as hp
import numpy as np

from astropy.coordinates import SkyCoord
from regions import PixCoord, PolygonSkyRegion
import astropy.wcs as world_coordinate_system
import astropy.units as u

from . import pixel_margins as pm


def get_margin_scale(pixel_order, margin_threshold=0.1):
    """Get the scale value need to expand the pixel bounding box to include the `margin_threshold`.

    Args:
        pixel_order (int): the order of the pixel to which we're calculating the margin region for.
        margin_threshold (float): the size of the border region in degrees.
    Returns:
        a float representing the scale factor.
    """
    if margin_threshold <= 0.0:
        raise ValueError("margin_threshold must be greater than 0.")

    resolution = hp.nside2resol(2**pixel_order, arcmin=True) / 60.0
    resolution_and_thresh = resolution + (margin_threshold)
    margin_area = resolution_and_thresh**2
    pixel_area = hp.pixelfunc.nside2pixarea(2**pixel_order, degrees=True)
    scale = margin_area / pixel_area
    return scale


def get_margin_bounds_and_wcs(pixel_order, pix, scale, step=10):
    """Get the astropy `regions.PolygonPixelRegion` and `astropy.wcs` objects
        for a given margin bounding box scale.

    Args:
        pixel_order (int): the order of the pixel to which we're calculating the margin region for.
        pix (int): the healpixel which we're calculating the margin region for.
        scale (float): the scale factor to apply to the given healpixel.
        step (int): the amount of samples of one side of the given healpixel's boundaries.
            total samples taken = 4 * step.
    Returns:
        polygons (list of tuples): a list of obj:`regions.PolygonPixelRegion` and obj:`wcs.WCS`
            tuples, covering the full area of the given healpixels scaled up area.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    pixel_boundaries = hp.vec2dir(
        hp.boundaries(2**pixel_order, pix, step=step, nest=True), lonlat=True
    )

    # find the translation values to keep the bounding box
    # centered around the orignal healpixel.
    n_samples = len(pixel_boundaries[0])
    centroid_lon = np.sum(pixel_boundaries[0]) / n_samples
    centroid_lat = np.sum(pixel_boundaries[1]) / n_samples
    translate_lon = centroid_lon - (centroid_lon * scale)
    translate_lat = centroid_lat - (centroid_lat * scale)

    affine_matrix = np.array(
        [[scale, 0, translate_lon], [0, scale, translate_lat], [0, 0, 1]]
    )

    # convert the orignal boundary coordinates into
    # a homogenous coordinate space (3-dim)
    homogeneous = np.ones((3, n_samples))
    homogeneous[0] = pixel_boundaries[0]
    homogeneous[1] = pixel_boundaries[1]

    transformed_bounding_box = np.matmul(affine_matrix, homogeneous)

    # if the transform places the declination of any points outside of
    # the range 90 > dec > -90, change it to a proper dec value.
    transformed_bounding_box[1] = np.clip(transformed_bounding_box[1], -90., 90.)

    min_ra = np.min(transformed_bounding_box[0])
    max_ra = np.max(transformed_bounding_box[0])
    min_dec = np.min(transformed_bounding_box[1])
    max_dec = np.max(transformed_bounding_box[1])

    # one arcsecond
    pix_size = 0.0002777777778

    ra_naxis = int((max_ra - min_ra) / pix_size)
    dec_naxis = int((max_dec - min_dec) / pix_size)

    polygons = []
    # for k < 2, the size of the bounding boxes breaks the regions
    # code, so we subdivide the pixel into multiple parts with
    # independent wcs.
    if pixel_order < 2:
        # k == 0 -> 16 subdivisions, k == 1 -> 4 subdivisions
        divs = 4 ** (2 - pixel_order)
        div_len = int((step * 4) / divs)
        for i in range(divs):
            j = i * div_len
            # get a `div_len + 1``  subset of the boundaries
            # inclusive of the first element of the next slice
            # so that we don't have any gaps in our boundary area.
            lon = list(transformed_bounding_box[0][j : j + div_len + 1])
            lat = list(transformed_bounding_box[1][j : j + div_len + 1])

            # in the last div, include the first data point
            # to ensure that we cover the whole area
            if i == divs - 1:
                lon.append(transformed_bounding_box[0][0])
                lat.append(transformed_bounding_box[1][0])

            lon.append(centroid_lon)
            lat.append(centroid_lat)

            ra_axis = int(ra_naxis / (2 ** (2 - pixel_order)))
            dec_axis = int(dec_naxis / (2 ** (2 - pixel_order)))

            wcs_partial = world_coordinate_system.WCS(naxis=2)
            wcs_partial.wcs.crpix = [1, 1]
            wcs_partial.wcs.crval = [lon[0], lat[0]]
            wcs_partial.wcs.cunit = ["deg", "deg"]
            wcs_partial.wcs.ctype = ["RA---TAN", "DEC--TAN"]
            wcs_partial.wcs.cdelt = [pix_size, pix_size]
            wcs_partial.array_shape = [ra_axis, dec_axis]

            vertices = SkyCoord(lon, lat, unit="deg")
            sky_region = PolygonSkyRegion(vertices=vertices)
            polygons.append((sky_region.to_pixel(wcs_partial), wcs_partial))
    else:
        wcs_margin = world_coordinate_system.WCS(naxis=2)
        wcs_margin.wcs.crpix = [1, 1]
        wcs_margin.wcs.crval = [min_ra, min_dec]
        wcs_margin.wcs.cunit = ["deg", "deg"]
        wcs_margin.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        wcs_margin.wcs.cdelt = [pix_size, pix_size]
        wcs_margin.array_shape = [ra_naxis, dec_naxis]

        vertices = SkyCoord(
            transformed_bounding_box[0], transformed_bounding_box[1], unit="deg"
        )
        sky_region = PolygonSkyRegion(vertices=vertices)
        polygon_region = sky_region.to_pixel(wcs_margin)
        polygons = [(polygon_region, wcs_margin)]

    return polygons


def check_margin_bounds(r_asc, dec, poly_and_wcs):
    """Get the astropy `regions.PolygonPixelRegion` and `astropy.wcs` objects
        for a given margin bounding box scale.

    Args:
        r_asc (:obj:`np.array`): one dimmensional array representing the ra of a
            given set of points.
        dec (:obj:`np.array`): one dimmensional array representing the dec of a
            given set of points.
        polygons (list of tuples): a list of obj:`regions.PolygonPixelRegion` and obj:`wcs.WCS`
            tuples, covering the full area of the given healpixels scaled up area.
            see get_margin_bounds_and_wcs for more details.
    Returns:
        obj:numpy.array of boolean values corresponding to the ra and dec coordinates
            checked against whether a given point is within any of the provided polygons.
    """
    sky_coords = SkyCoord(r_asc, dec, unit="deg")
    bound_vals = []
    for poly, wcs in poly_and_wcs:
        x_coords, y_coords = world_coordinate_system.utils.skycoord_to_pixel(
            sky_coords, wcs
        )
        pix_coords = PixCoord(x_coords, y_coords)
        vals = poly.contains(pix_coords)
        bound_vals.append(vals)
    return np.array(bound_vals).any(axis=0)

def check_polar_margin_bounds(r_asc, dec, order, pix, margin_order, margin_threshold, step=1000):
    """Given a set of ra and dec values that are around one of the poles,
        determine if they are within `margin_threshold` of a provided
        partition pixel. This method helps us solve the edge cases that
        occur for margin bounding around the poles.

    Args:
        r_asc (:obj:`np.array`): one dimmensional array representing the ra of a
            given set of points.
        dec (:obj:`np.array`): one dimmensional array representing the dec of a
            given set of points.
        order (int): the healpix order of the provided partition pixel.
        pix (int): the partition healpixel that we are creating the margin cache of.
        margin_order (int): the healpix order of our pre-generated margin pixels.
        margin_threshold (float): the size of the border region in degrees.
        step (int): the total number of samples taken per side of the partition
            pixel `pix`. Only a small subset of these points will actually be used
            to check distance from the pixel, but step can be increased to get
            more granularity in the `margin_threshold` angular distance measurements.
    Returns:
        obj:numpy.array of boolean values corresponding to the ra and dec coordinates
            checked against whether a given point is within any of the provided polygons.
    """
    polar, pole = pm.pixel_is_polar(order, pix)

    if not polar:
        raise ValueError("provided healpixel must be polar")

    part_pix_res = hp.nside2resol(2**order)
    marg_pix_res = hp.nside2resol(2**margin_order)

    # get the approximate number of boundary samples to cover a highest_k pixel
    # on the boundary of the main pixel
    boundary_range = int((marg_pix_res / part_pix_res) * step)
    pixel_boundaries = hp.vec2dir(
        hp.boundaries(2**order, pix, step=step, nest=True), 
        lonlat=True
    )

    if pole == "North":
        end = len(pixel_boundaries[0])
        east_ra = pixel_boundaries[0][0:boundary_range+1]
        east_dec = pixel_boundaries[1][0:boundary_range+1]

        west_ra = pixel_boundaries[0][end-boundary_range:end]
        west_dec = pixel_boundaries[1][end-boundary_range:end]

        bound_ra = np.concatenate((east_ra, west_ra), axis=None)
        bound_dec = np.concatenate((east_dec, west_dec), axis=None)
        polar_boundaries = np.array([bound_ra, bound_dec])
    else:
        start = (2 * step) - boundary_range
        end = (2 * step) + boundary_range + 1
        south_ra = pixel_boundaries[0][start:end]
        south_dec = pixel_boundaries[1][start:end]
        polar_boundaries = np.array([south_ra, south_dec])

    # healpy.boundaries sometimes returns dec values greater than 90, especially
    # when taking many samples...
    polar_boundaries[1] = np.clip(polar_boundaries[1], -90., 90.)

    sky_coords = SkyCoord(r_asc, dec, unit='deg')

    checks = []
    for i in range(len(polar_boundaries[0])):
        lon = polar_boundaries[0][i]
        lat = polar_boundaries[1][i]
        bound_coord = SkyCoord(lon, lat, unit='deg')

        ang_dist = bound_coord.separation(sky_coords)
        checks.append(ang_dist <= margin_threshold*u.deg)

    return np.array(checks).any(axis=0)
