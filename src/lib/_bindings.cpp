#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "pixel_math.h"

namespace py = pybind11;

PYBIND11_MODULE(_hipscat, m) {
    m.def("generate_alignment", &hipscat::generate_alignment);
}