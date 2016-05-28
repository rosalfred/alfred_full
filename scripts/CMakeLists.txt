##############################################################################
# Installs
##############################################################################

# Rosrunnable installation of scripts
catkin_install_python(
  PROGRAMS alfred_tools
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
