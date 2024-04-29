cmake_minimum_required(VERSION 3.10)
if(${CMAKE_VERSION} VERSION_GREATER 3.10)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
endif()
message(STATUS "CMake version: ${CMAKE_MAJOR_VERSION}")
message(STATUS "CMake minor: ${CMAKE_MINOR_VERSION}")
project(hipscat VERSION 1.0)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}")
set(CMAKE_BINARY_DIR "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_BUILD_TYPE "RelWithDebInfo")
set(CMAKE_VERBOSE_MAKEFILE ON)

if (DEFINED ENV{PYTHON_VERSION_REQUIRED})
  message(STATUS "Python version required: $ENV{PYTHON_VERSION_REQUIRED}")
  find_package(Python3 $ENV{PYTHON_VERSION_REQUIRED} EXACT COMPONENTS Development.Module Interpreter REQUIRED)
else()
  find_package(Python3 COMPONENTS Development.Module Interpreter REQUIRED)
endif()

message(STATUS "Python version: ${Python3_VERSION}")
message(STATUS "Python libraries: ${Python3_LIBRARY}")
message(STATUS "Python executable: ${Python3_EXECUTABLE}")
message(STATUS "Python included_dir: ${Python3_INCLUDE_DIR}")


# Set source directory
set(SOURCE_DIR "./src/lib")
# Tell CMake that headers are also in SOURCE_DIR
include_directories(${SOURCE_DIR})
#provide exhaustive list of source files, as recommended by
#CMake developers
set(SOURCES
  "${SOURCE_DIR}/pixel_math.cpp"
)

#! May need to remove the -march=native, this may cause problems in the compiled, pip installable, version.
# Remove flags that break mac compilation with g++-13
add_compile_options("-Ofast" "-ffast-math" "-fno-finite-math-only" "-fsigned-zeros" "-fno-associative-math" "-fno-inline" "-march=native" "-mtune=native" "-funroll-loops" "-fomit-frame-pointer" "-finline" "-ftree-vectorize")
if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(ENV{CC} "/usr/local/opt/llvm/bin/clang")
    set(ENV{CXX} "/usr/local/opt/llvm/bin/clang++")
    set(ENV{LDFLAGS} "-L/usr/local/opt/llvm/lib")
    set(ENV{CPPFLAGS} "-I/usr/local/opt/llvm/include")
    set(CMAKE_CPP_COMPILER "clang++")
    set(CMAKE_C_COMPILER "clang")
else()
    add_compile_options("-mno-vzeroupper" "-mavx2" "-floop-unroll-and-jam" )
endif()

# only set these flags if in `INCLUDE_COVERAGE` env var is set (to any value)
if(DEFINED ENV{INCLUDE_COVERAGE})
  message(STATUS "Building with code coverage enabled.")
  SET(GCC_COVERAGE_COMPILE_FLAGS "-g -O0 -coverage -fprofile-arcs -ftest-coverage")
  SET(GCC_COVERAGE_LINK_FLAGS    "-coverage -lgcov")
  SET( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_COVERAGE_COMPILE_FLAGS}" )
  SET( CMAKE_EXE_LINKER_FLAGS  "${CMAKE_EXE_LINKER_FLAGS} ${GCC_COVERAGE_LINK_FLAGS}" )
endif()

add_library(hipscatlib STATIC ${SOURCES})

# Build the hipscat executables
#add_executable(pixel_math
#  "${SOURCE_DIR}/pixel_math.cpp"
#  )

# Build the python module
add_subdirectory(extern/pybind11/)
pybind11_add_module(_hipscat ${SOURCES} "${SOURCE_DIR}/_bindings.cpp")
target_compile_definitions(_hipscat
                           PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
target_link_libraries(_hipscat PRIVATE pybind11::module)

install(TARGETS RUNTIME DESTINATION bin)