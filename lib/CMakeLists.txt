cmake_minimum_required(VERSION 3.2.2)
project(StateReporterLib)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_BUILD_TYPE Debug)

if (BUILD_SHARED_LIBS STREQUAL "ON")
    set(LIBRARY_TYPE SHARED)
elseif(BUILD_STATIC_LIBS STREQUAL "ON")
    set(LIBRARY_TYPE STATIC)
else()
    set(LIBRARY_TYPE STATIC)
    set(CMAKE_LINK_LIBRARY_SUFFIX .lib)
endif()

set(SOURCES
        StateReporter.cpp
        StateReporterC.cpp
)

include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}
)

add_library(
        StateReporterLib
        ${LIBRARY_TYPE}
        ${SOURCES}
)

if (LIBRARY_TYPE STREQUAL "STATIC")
    set_property(TARGET StateReporterLib PROPERTY POSITION_INDEPENDENT_CODE ON)
endif ()

if (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
    set(THREADS_PREFER_PTHREAD_FLAG ON)
    find_package(Threads REQUIRED)
    target_link_libraries (StateReporterLib ${CMAKE_THREAD_LIBS_INIT})
endif()
