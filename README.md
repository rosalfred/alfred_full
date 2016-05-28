Alfred full stack
===

Prepare
---

Create a directory for the workspace.
Go to the workspace directory and type in terminal :

    mkdir ./src
    git clone ssh://git@git.tactfactory.com:2222/projetx/alfred-full.git ./src/alfred_full
    source {your rosjava setup.bash}
    catkin_make
    source devel/setup.bash

Installation & Update
---

You can now use alfred script to install or update Alfred ROS packages

    alfred_tools
