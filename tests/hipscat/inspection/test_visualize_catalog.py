import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import pytest
from astropy.coordinates import Angle, SkyCoord
from astropy.visualization.wcsaxes.frame import EllipticalFrame
from matplotlib.cm import get_cmap
from matplotlib.colors import LogNorm, Normalize
from mocpy import WCS
from mocpy.moc.plot.culling_backfacing_cells import from_moc
from mocpy.moc.plot.fill import compute_healpix_vertices

from hipscat.inspection import plot_pixels
from hipscat.inspection.visualize_catalog import cull_from_pixel_map, plot_healpix_map

# pylint: disable=no-member


DEFAULT_CMAP_NAME = "viridis"
DEFAULT_FOV = (320 * u.deg, 160 * u.deg)
DEFAULT_CENTER = SkyCoord(0, 0, unit="deg", frame="icrs")
DEFAULT_COORDSYS = "icrs"
DEFAULT_ROTATION = Angle(0, u.degree)
DEFAULT_PROJECTION = "MOL"


def test_plot_healpix_pixels():
    order = 3
    length = 10
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert len(paths) == length
    assert col.get_cmap() == get_cmap(DEFAULT_CMAP_NAME)
    assert isinstance(col.norm, Normalize)
    assert col.norm.vmin == min(map)
    assert col.norm.vmax == max(map)
    assert col.colorbar is not None
    assert col.colorbar.cmap == get_cmap(DEFAULT_CMAP_NAME)
    assert col.colorbar.norm == col.norm
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    for path, ipix in zip(paths, ipix):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)


def test_plot_healpix_pixels_different_order():
    order = 6
    length = 1000
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w

    all_verts, all_codes = compute_healpix_vertices(order, ipix, wcs)
    for i, (path, ipix) in enumerate(zip(paths, ipix)):
        verts, codes = all_verts[i * 5 : (i + 1) * 5], all_codes[i * 5 : (i + 1) * 5]
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)


def test_order_0_pixels_split_to_order_3():
    map_value = 0.5
    order_0_pix = 4
    ipix = np.array([order_0_pix])
    map = np.array([map_value])
    depth = np.array([0])
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    length = 4**3
    order3_ipix = np.arange(length * order_0_pix, length * (order_0_pix + 1))
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    all_verts, all_codes = compute_healpix_vertices(3, order3_ipix, wcs)
    for i, (path, ipix) in enumerate(zip(paths, order3_ipix)):
        verts, codes = all_verts[i * 5 : (i + 1) * 5], all_codes[i * 5 : (i + 1) * 5]
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), np.full(length, fill_value=map_value))


def test_edge_pixels_split_to_order_7():
    map_value = 0.5
    order_0_pix = 2
    ipix = np.array([order_0_pix])
    map = np.array([map_value])
    depth = np.array([0])
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth)
    assert len(ax.collections) == 1
    edge_pixels = {0: [order_0_pix]}
    for o in range(1, 8):
        edge_pixels[o] = [p * 4 + i for p in edge_pixels[o - 1] for i in (2, 3)]
    non_edge_pixels = {}
    pixels_ord3 = np.arange(4**3 * order_0_pix, 4**3 * (order_0_pix + 1))
    non_edge_pixels[3] = pixels_ord3[~np.isin(pixels_ord3, edge_pixels[3])]
    for o in range(4, 8):
        pixels_ord = np.concatenate([np.arange(4 * pix, 4 * (pix + 1)) for pix in edge_pixels[o - 1]])
        non_edge_pixels[o] = pixels_ord[~np.isin(pixels_ord, edge_pixels[o])]
    col = ax.collections[0]
    paths = col.get_paths()
    length = sum([len(x) for x in non_edge_pixels.values()])
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    ords = np.concatenate([np.full(len(x), fill_value=o) for o, x in non_edge_pixels.items()])
    pixels = np.concatenate([np.array(x) for _, x in non_edge_pixels.items()])
    for path, o, pix in zip(paths, ords, pixels):
        verts, codes = compute_healpix_vertices(o, np.array([pix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), np.full(length, fill_value=map_value))


def test_cull_from_pixel_map():
    order = 1
    ipix = np.arange(12 * 4**order)
    map = np.arange(12 * 4**order)
    map_dict = {order: (ipix, map)}
    fig = plt.figure(figsize=(10, 5))
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    culled_dict = cull_from_pixel_map(map_dict, wcs)
    mocpy_culled = from_moc({str(order): ipix}, wcs)
    for o, (pixels, m) in culled_dict.items():
        np.testing.assert_array_equal(pixels, mocpy_culled[str(o)])
        map_indices = pixels >> (2 * (o - order))
        np.testing.assert_array_equal(m, map[map_indices])


def test_plot_healpix_map():
    order = 1
    ipix = np.arange(12 * 4**order)
    map = np.arange(12 * 4**order)
    fig, ax = plot_healpix_map(map)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    map_dict = {order: (ipix, map)}
    culled_dict = cull_from_pixel_map(map_dict, wcs)
    all_vals = []
    start_i = 0
    for o, (pixels, m) in culled_dict.items():
        all_verts, all_codes = compute_healpix_vertices(o, pixels, wcs)
        for i, pix in enumerate(pixels):
            verts, codes = all_verts[i * 5 : (i + 1) * 5], all_codes[i * 5 : (i + 1) * 5]
            path = paths[start_i + i]
            np.testing.assert_array_equal(path.vertices, verts)
            np.testing.assert_array_equal(path.codes, codes)
        all_vals.append(m)
        start_i += len(pixels)
    np.testing.assert_array_equal(np.concatenate(all_vals), col.get_array())


def test_plot_wcs_params():
    order = 3
    length = 10
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(
        map,
        ipix=ipix,
        depth=depth,
        fov=(100 * u.deg, 50 * u.deg),
        center=SkyCoord(10, 10, unit="deg", frame="icrs"),
        projection="AIT",
    )
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=(100 * u.deg, 50 * u.deg),
        center=SkyCoord(10, 10, unit="deg", frame="icrs"),
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection="AIT",
    ).w
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)
    assert ax.get_transform("icrs") is not None


def test_plot_wcs():
    order = 3
    length = 10
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig = plt.figure(figsize=(10, 5))
    wcs = WCS(
        fig,
        fov=(100 * u.deg, 50 * u.deg),
        center=SkyCoord(10, 10, unit="deg", frame="icrs"),
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection="AIT",
    ).w
    fig2, ax = plot_healpix_map(map, ipix=ipix, depth=depth, fig=fig, wcs=wcs)
    assert fig2 is fig
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert len(paths) == length
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)
    assert ax.get_transform("icrs") is not None


def test_plot_wcs_and_ax():
    order = 3
    length = 10
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig = plt.figure(figsize=(10, 5))
    wcs = WCS(
        fig,
        fov=(100 * u.deg, 50 * u.deg),
        center=SkyCoord(10, 10, unit="deg", frame="icrs"),
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection="AIT",
    ).w
    ax = fig.add_subplot(1, 1, 1, projection=wcs, frame_class=EllipticalFrame)
    assert len(ax.collections) == 0
    fig2, ax2 = plot_healpix_map(map, ipix=ipix, depth=depth, fig=fig, wcs=wcs, ax=ax)
    assert fig2 is fig
    assert ax2 is ax
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert len(paths) == length
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)
    assert ax.get_transform("icrs") is not None


def test_plot_ax_no_wcs():
    order = 3
    length = 10
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig = plt.figure(figsize=(10, 5))
    wcs = WCS(
        fig,
        fov=(100 * u.deg, 50 * u.deg),
        center=SkyCoord(10, 10, unit="deg", frame="icrs"),
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection="AIT",
    ).w
    ax = fig.add_subplot(1, 1, 1, projection=wcs, frame_class=EllipticalFrame)
    with pytest.raises(ValueError):
        plot_healpix_map(map, ipix=ipix, depth=depth, fig=fig, ax=ax)


def test_plot_cmaps():
    order = 3
    length = 10
    cmap_name = "plasma"
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth, cmap=cmap_name)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert col.get_cmap() == get_cmap(cmap_name)
    assert col.colorbar is not None
    assert col.colorbar.cmap == get_cmap(cmap_name)
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)

    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth, cmap=get_cmap(cmap_name))
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert col.get_cmap() == get_cmap(cmap_name)
    assert col.colorbar is not None
    assert col.colorbar.cmap == get_cmap(cmap_name)
    assert len(paths) == length
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)


def test_plot_norm():
    order = 3
    length = 10
    norm = LogNorm()
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth, norm=norm)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    paths = col.get_paths()
    assert col.norm == norm
    assert col.colorbar is not None
    assert col.colorbar.norm == norm
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)


def test_plot_no_cbar():
    order = 3
    length = 10
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth, cbar=False)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    assert col.colorbar is None
    paths = col.get_paths()
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)


def test_plot_kwargs():
    order = 3
    length = 10
    label = "test"
    ipix = np.arange(length)
    map = np.arange(length)
    depth = np.full(length, fill_value=order)
    fig, ax = plot_healpix_map(map, ipix=ipix, depth=depth, label=label)
    assert len(ax.collections) == 1
    col = ax.collections[0]
    assert col.get_label() == label
    paths = col.get_paths()
    assert len(paths) == length
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    for path, ipix in zip(paths, np.arange(len(map))):
        verts, codes = compute_healpix_vertices(order, np.array([ipix]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), map)


def test_catalog_plot(small_sky_order1_catalog):
    fig, ax = plot_pixels(small_sky_order1_catalog)
    pixels = sorted(small_sky_order1_catalog.get_healpix_pixels())
    order_3_pixels = [p for pix in pixels for p in pix.convert_to_higher_order(3 - pix.order)]
    order_3_orders = [pix.order for pix in pixels for _ in pix.convert_to_higher_order(3 - pix.order)]
    col = ax.collections[0]
    paths = col.get_paths()
    assert len(paths) == len(order_3_pixels)
    wcs = WCS(
        fig,
        fov=DEFAULT_FOV,
        center=DEFAULT_CENTER,
        coordsys=DEFAULT_COORDSYS,
        rotation=DEFAULT_ROTATION,
        projection=DEFAULT_PROJECTION,
    ).w
    for p, path in zip(order_3_pixels, paths):
        verts, codes = compute_healpix_vertices(p.order, np.array([p.pixel]), wcs)
        np.testing.assert_array_equal(path.vertices, verts)
        np.testing.assert_array_equal(path.codes, codes)
    np.testing.assert_array_equal(col.get_array(), np.array(order_3_orders))
    assert ax.get_title() == f"Catalog pixel density map - {small_sky_order1_catalog.catalog_name}"
