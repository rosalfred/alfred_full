cmake_minimum_required(VERSION 2.8.3)
project(alfred_full)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS)

###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if you package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES media-full
#  CATKIN_DEPENDS media media_cameranetwork_driver media_onkyo_driver media_samsung_driver media_xbmc_driver media_xbmc_driver_py
#  DEPENDS system_lib
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
# include_directories(include)
include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_python_setup()

add_subdirectory(scripts)

file(WRITE ${CATKIN_DEVEL_PREFIX}/alfred/alfred_full "Java")
install(FILES ${CATKIN_DEVEL_PREFIX}/alfred/alfred_full DESTINATION alfred)
