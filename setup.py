from glob import glob
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "hipscat_cpp",
        sorted(glob("src/hipscat_cpp/*.cpp")),  # Sort source files for reproducibility
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    use_scm_version=True,
)