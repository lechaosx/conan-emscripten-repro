cmake_minimum_required(VERSION 3.26)

project(repro_sizeof_void_p)

if(NOT DEFINED CMAKE_SIZEOF_VOID_P)
	message(FATAL_ERROR "CMAKE_SIZEOF_VOID_P is not defined")
endif()

message(STATUS "Pointer size is ${CMAKE_SIZEOF_VOID_P}")

add_library(dummy STATIC dummy.cpp)