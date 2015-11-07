#!/usr/bin/env python

import os
import subprocess
import sys

os.chdir("./src"
subprocess.call(['wstool'])

os.chdir("..")
subprocess.call(['genjava_message_artifacts', '-p', 'media_msgs', 'heater_msgs'])
subprocess.call(['catkin_make'])

os.chdir("./src")

path = os.getcwd()

for fn in os.listdir('.'):
    dir = path + "/" + fn + "/"
    print (dir)
    if not os.path.isfile(dir) and os.path.isfile(dir + "build.gradle"):
        os.chdir(dir)
        subprocess.call(['./gradlew', 'cleanEclipse', 'eclipse'])
