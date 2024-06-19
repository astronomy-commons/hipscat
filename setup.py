import os
import pathlib
import platform
import re
import subprocess
import sys
from distutils.version import LooseVersion

from setuptools import Command, Extension, setup
from setuptools.command.build_ext import build_ext

here = pathlib.Path(__file__).parent.resolve()
# Get the long description from the README file


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r"version\s*([\d.]+)", out.decode()).group(1))
            if cmake_version < "3.1.0":
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = [
            "-DCMAKE_INSTALL_PREFIX=${CMAKE_SOURCE_DIR}",
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir,
            "-DPYTHON_EXECUTABLE=" + sys.executable,
        ]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        if platform.system() == "Windows":
            cmake_args += [f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"]
            if sys.maxsize > 2**32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
        else:
            cmake_args += ["-DCMAKE_BUILD_TYPE:STRING=" + cfg]
            build_args += ["--", "-j2"]

        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()
        )
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=self.build_temp)
        subprocess.check_call(["cmake", "--install", "."], cwd=self.build_temp)
        print()  # Add an empty line for cleaner output


setup(
    name="hipscat",
    author="LINCC Frameworks",
    author_email="lincc-frameworks-team@lists.lsst.org",
    url="https://github.com/astronomy-commons/hipscat/",
    # add extension module
    ext_modules=[CMakeExtension("hipscat._hipscat")],
    include_package_data=True,
    # add custom build_ext command
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    python_requires=">=3.9",
    extras_require={"test": "pytest"},
)
