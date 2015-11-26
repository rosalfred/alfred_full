##############################################################################
# Installs
##############################################################################

# Rosrunnable installation of scripts
catkin_install_python(
  PROGRAMS alfred_update_packages
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
