import healpy as hp

# pylint: disable=missing-function-docstring

## Arithmetic conversions


def nside2order(param):
    return hp.nside2order(param)


def order2nside(param):
    return hp.order2nside(param)


def npix2nside(param):
    return hp.npix2nside(param)


def nside2npix(param):
    return hp.nside2npix(param)


def order2npix(param):
    return hp.order2npix(param)


def npix2order(param):
    return hp.npix2order(param)


def nside2resol(*args, **kwargs):
    return hp.nside2resol(*args, **kwargs)


def nside2pixarea(*args, **kwargs):
    return hp.nside2pixarea(*args, **kwargs)


def ang2pix(*args, **kwargs):
    return hp.ang2pix(*args, **kwargs)


def ring2nest(*args, **kwargs):
    return hp.ring2nest(*args, **kwargs)


def nest2ring(*args, **kwargs):
    return hp.nest2ring(*args, **kwargs)


def unseen_pixel():
    return hp.pixelfunc.UNSEEN


## Query


def query_strip(*args, **kwargs):
    return hp.query_strip(*args, **kwargs)


def query_polygon(*args, **kwargs):
    return hp.query_polygon(*args, **kwargs)


def boundaries(*args, **kwargs):
    return hp.boundaries(*args, **kwargs)


def get_all_neighbours(*args, **kwargs):
    return hp.get_all_neighbours(*args, **kwargs)


## Coordinate conversion


def ang2vec(*args, **kwargs):
    return hp.ang2vec(*args, **kwargs)


def pix2ang(*args, **kwargs):
    return hp.pix2ang(*args, **kwargs)


def vec2dir(*args, **kwargs):
    return hp.vec2dir(*args, **kwargs)


def pix2xyf(*args, **kwargs):
    return hp.pix2xyf(*args, **kwargs)


## FITS
def read_map(*args, **kwargs):
    return hp.read_map(*args, **kwargs)


def write_map(*args, **kwargs):
    return hp.write_map(*args, **kwargs)
