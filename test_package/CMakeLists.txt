cmake_minimum_required(VERSION 3.6)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# configure_file("google-services.json" "${CMAKE_CURRENT_BINARY_DIR}/bin/google-services.json" COPYONLY)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads MODULE REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS} Threads::Threads)

set_target_properties(example
    PROPERTIES
    OUTPUT_NAME test
    CXX_STANDARD 11
)
