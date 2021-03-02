cmake_minimum_required(VERSION 3.8)

if (CMAKE_CURRENT_SOURCE_DIR STREQUAL CMAKE_SOURCE_DIR)
    project(generate_data)

    find_package(xtensor-zarr REQUIRED CONFIG)
    set(XTENSOR_ZARR_INCLUDE_DIR ${xtensor_zarr_INCLUDE_DIRS})
endif ()

include(CheckCXXCompilerFlag)

string(TOUPPER "${CMAKE_BUILD_TYPE}" U_CMAKE_BUILD_TYPE)

if (CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR CMAKE_CXX_COMPILER_ID MATCHES "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Intel")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native -Wunused-parameter -Wextra -Wreorder -Wconversion -Wsign-conversion")
    CHECK_CXX_COMPILER_FLAG("-std=c++14" HAS_CPP14_FLAG)

    if (HAS_CPP14_FLAG)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
    else()
        message(FATAL_ERROR "Unsupported compiler -- xtensor requires C++14 support!")
    endif()
endif()

if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc /MP /bigobj")
    set(CMAKE_EXE_LINKER_FLAGS /MANIFEST:NO)
endif()

set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH}" "${CMAKE_SOURCE_DIR}/modules")

find_package(Threads)
find_package(xtensor-io)
find_package(zarray)

find_package(OIIO REQUIRED)
include_directories(${OIIO_INCLUDE_DIRS})
target_include_directories(xtensor-zarr
    INTERFACE
    $<BUILD_INTERFACE:${OIIO_INCLUDE_DIRS}>
)
target_link_libraries(xtensor-zarr
    INTERFACE
    ${OIIO_LIBRARIES}
)

find_package(ZLIB REQUIRED)
include_directories(${ZLIB_INCLUDE_DIRS})
target_include_directories(xtensor-zarr
    INTERFACE
    $<BUILD_INTERFACE:${ZLIB_INCLUDE_DIRS}>
)
target_link_libraries(xtensor-zarr
    INTERFACE
    ${ZLIB_LIBRARIES}
)

find_package(Blosc REQUIRED)
include_directories(${Blosc_INCLUDE_DIRS})
target_include_directories(xtensor-zarr
    INTERFACE
    $<BUILD_INTERFACE:${Blosc_INCLUDE_DIRS}>
)
target_link_libraries(xtensor-zarr
    INTERFACE
    ${Blosc_LIBRARIES}
)

set(XTENSOR_ZARR_GENERATE_DATA
    src/main.cpp)

add_executable(run_xtensor_zarr ${XTENSOR_ZARR_GENERATE_DATA} ${XTENSOR_ZARR_HEADERS})

if(DEFINED CMAKE_INSTALL_PREFIX)
    set_target_properties(run_xtensor_zarr
        PROPERTIES
        INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib;${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}"
        BUILD_WITH_INSTALL_RPATH ON
    )
endif()

target_link_libraries(run_xtensor_zarr
    PUBLIC
    xtensor-zarr
    ${CMAKE_DL_LIBS}
    ${CMAKE_THREAD_LIBS_INIT}
)

target_include_directories(run_xtensor_zarr PRIVATE ${XTENSOR_ZARR_INCLUDE_DIR})

add_custom_target(run
    COMMAND run_xtensor_zarr
    DEPENDS run_xtensor_zarr)
