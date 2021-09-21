cmake_minimum_required(VERSION 3.18)

project(lycon2)

include(cmake/Lycon2Utils.cmake)

set(LYCON2_SOURCES
  src/lycon/io/base.cc
  src/lycon/io/bitstream.cc
  src/lycon/io/exif.cc
  src/lycon/io/io.cc
  src/lycon/io/jpeg.cc
  src/lycon/io/png.cc

  src/lycon/mat/allocator.cc
  src/lycon/mat/convert.cc
  src/lycon/mat/copy.cc
  src/lycon/mat/io_array.cc
  src/lycon/mat/iterator.cc
  src/lycon/mat/mat.cc
  src/lycon/mat/umat_data.cc

  src/lycon/transform/resize.cc
  src/lycon/transform/rotate.cc

  src/lycon/util/alloc.cc
  src/lycon/util/color.cc
  src/lycon/util/file.cc
  src/lycon/util/hardware.cc
  src/lycon/util/parallel_pthreads.cc
  src/lycon/util/parallel.cc
  src/lycon/util/singleton.cc
  src/lycon/util/string.cc
  src/lycon/util/tls.cc
)

set(LYCON2_PYTHON_SOURCES
  src/lycon/python/interop.cc
  src/lycon/python/module.cc
)

set(CMAKE_MACOSX_RPATH TRUE)

# Build options
lycon2_option(LYCON2_BUILD_STATIC "Build Lycon2 as a static library" ON)
lycon2_option(LYCON2_BUILD_PYTHON "Build the Python native extension" ON)
lycon2_option(LYCON2_NUMPY_ALLOCATOR_BY_DEFAULT "Use the NumPy allocator by default" ${LYCON2_BUILD_PYTHON})
# Enabling this can avoid libstdc++ compatibility issues under environments like Conda
lycon2_option(LYCON2_STATIC_LIBSTDCPP "Statically link against libstdc++" ON IF NOT APPLE)

include_directories(src)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -march=native -O3 -fPIC -DNDEBUG -pthread")
if(LYCON2_STATIC_LIBSTDCPP)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static-libstdc++")
endif()

# If enabled, use the NumPy allocator as the default Mat allocator
if(LYCON2_NUMPY_ALLOCATOR_BY_DEFAULT)
  add_definitions(-DLYCON2_USE_NUMPY_ALLOCATOR_BY_DEFAULT)
endif()

# The main library
if(LYCON2_BUILD_STATIC)
  add_library(lycon2 STATIC ${LYCON2_SOURCES})
else()
  add_library(lycon2 SHARED ${LYCON2_SOURCES})
endif()

# LibPNG
find_package(PNG REQUIRED)
include_directories(${PNG_INCLUDE_DIR})
target_link_libraries(lycon2 ${PNG_LIBRARY})

# LibJPEG
find_package(JPEG REQUIRED)
include_directories(${JPEG_INCLUDE_DIR})
target_link_libraries(lycon2 ${JPEG_LIBRARY})

# The Python extension
if (LYCON2_BUILD_PYTHON)
  message(STATUS "Python3_EXECUTABLE:${Python3_EXECUTABLE}")
  if (UNIX AND NOT APPLE)
    find_package(Python3 COMPONENTS Interpreter Development.Module NumPy REQUIRED)
  endif ()
  if (APPLE)
    find_package(Python3 COMPONENTS Interpreter Development NumPy REQUIRED)
  endif ()

  message(STATUS "Python3_EXECUTABLE:${Python3_EXECUTABLE}")
  message(STATUS "Python3_LIBRARY_DIRS:${Python3_LIBRARY_DIRS}")
  message(STATUS "Python3_RUNTIME_LIBRARY_DIRS:${Python3_RUNTIME_LIBRARY_DIRS}")
  message(STATUS "Python3_LIBRARIES:${Python3_LIBRARIES}")
  message(STATUS "Python3_INCLUDE_DIRS:${Python3_INCLUDE_DIRS}")
  message(STATUS "Python3_NUMPY_INCLUDE_DIRS:${Python3_NumPy_INCLUDE_DIRS}")

  include_directories(${Python3_INCLUDE_DIRS})
  include_directories(${Python3_NumPy_INCLUDE_DIRS})

  add_library(pycon2 SHARED ${LYCON2_PYTHON_SOURCES})
  target_link_libraries(pycon2 lycon2 ${Python3_LIBRARIES})

  # NOTE(saumitro): Even on macOS, Python expects the ".so" suffix rather than ".dylib"
  set_target_properties(pycon2 PROPERTIES PREFIX "_" SUFFIX ".so" OUTPUT_NAME "lycon2")
endif()
