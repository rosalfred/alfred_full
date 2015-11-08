Alfred full stack
===

Installation
---

Create a directory for the workspace.
Go to the workspace directory and type in terminal :

    mkdir ./src
    
    echo "# IT IS UNLIKELY YOU WANT TO EDIT THIS FILE BY HAND,
    # UNLESS FOR REMOVING ENTRIES.
    # IF YOU WANT TO CHANGE THE ROS ENVIRONMENT VARIABLES 
    # USE THE rosinstall TOOL INSTEAD.
    # IF YOU CHANGE IT, USE rosinstall FOR THE CHANGES TO TAKE EFFECT
    - git: {local-name: alfred, uri: 'ssh://git@git.tactfactory.com:2222/projetx/alfred.git'}
    - git: {local-name: alfred_full, uri: 'ssh://git@git.tactfactory.com:2222/projetx/alfred-full.git'}
    - git: {local-name: rosbuilding_msgs, uri: 'ssh://git@git.tactfactory.com:2222/projetx/rosbuilding-msgs.git'}
    - git: {local-name: rosbuilding_msgs_java, uri: 'ssh://git@git.tactfactory.com:2222/projetx/rosbuilding-msgs-java.git'}
    - git: {local-name: rosjava_dynamic_reconfigure, uri: 'https://github.com/Theosakamg/rosjava_dynamic_reconfigure.git'}
    - git: {local-name: network_wakeonlan, uri: 'ssh://git@git.tactfactory.com:2222/projetx/network-wakeonlan.git'}
    - git: {local-name: network_zeroconf, uri: 'ssh://git@git.tactfactory.com:2222/projetx/network-zeroconf.git'}
    - git: {local-name: media_camera_ip_driver, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-camera-ip-driver.git'}
    - git: {local-name: common_driver, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-driver.git'}
    - git: {local-name: media_model, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-model.git'}
    - git: {local-name: media_msgs, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-msgs.git'}
    - git: {local-name: media_msgs_java, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-msgs-java.git'}
    - git: {local-name: media_onkyo_ip_driver, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-onkyo-ip-driver.git'}
    - git: {local-name: media_samsung_ip_driver, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-samsung-ip-driver.git'}
    - git: {local-name: media_xbmc_ip_driver, uri: 'ssh://git@git.tactfactory.com:2222/projetx/media-xbmc-ip-driver.git'}
    - git: {local-name: people_common, uri: 'ssh://git@git.tactfactory.com:2222/projetx/people-common.git'}" > ./src/.rosinstall

To install all sources of Alfred, type in terminal :

    cd ./src
    wstool update

To build all sources of Alfred, go to the root workspace directory and type in terminal :

    catkin_make
