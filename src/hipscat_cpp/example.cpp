#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

float adder(float a, float b) {
    return a + b;
}

PYBIND11_MODULE(hipscat_cpp, m) {
    m.def("adder", &adder, "A function that adds two numbers");
}
