# Software License Agreement
#
# Copyright (c) 2015, Mickael Gaillard.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

##############################################################################
# Imports
##############################################################################

from __future__ import print_function
import argparse
import os
import subprocess

import catkin_pkg.packages
import genjava
import wstool.wstool_cli

def standalone_parse_arguments(argv):
    parser = argparse.ArgumentParser(description='Update Alfred ROS packages from repository, build catkin and update eclipse project.')
    parser.add_argument('-p', '--package', action='store', nargs='*', default=[], help='a list of packages to update')
    parser.add_argument('-w', '--wstool', default=False, action='store_true', help='run wstool update (false)')
    parser.add_argument('-g', '--genmsgs', default=False, action='store_true', help='run generate_message_artifacts (false)')
    parser.add_argument('-c', '--catkin', default=False, action='store_true', help='run catkin_make (false)')
    parser.add_argument('-e', '--eclipse', default=False, action='store_true', help='update Eclipse project (false)')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='enable verbosity in debugging (false)')
    parser.add_argument('-f', '--fakeit', default=False, action='store_true', help='dont build, just list the packages it would update (false)')
    parsed_arguments = parser.parse_args(argv)
    return parsed_arguments

def standalone_main(argv):
    args = standalone_parse_arguments(argv[1:])
    UpdateUtils().init()
        
class UpdateUtils(object):
    setup_sh = 'devel/setup.sh'
    env_ros_package_path = 'ROS_PACKAGE_PATH'
    ros_install_prefix = '.rosinstall'
    alfred_full_path = 'src/alfred_full'
    msg_packages = ['rosbuilding_msgs', 'media_msgs', 'heater_msgs']

    def init(self):
        is_in_workspace = self.is_in_workspace() # in this case we are in workspace
        is_in_alfred_full = self.is_in_alfred_full() # if current directory is alfred_full
        
        if is_in_workspace:
            os.chdir(UpdateUtils.alfred_full_path)
            
        # in this case => error
        if not is_in_workspace and not is_in_alfred_full:
            self.log(LogLevel.ERROR, 'You are not in a ROS workspace. Exit.')
            sys.exit()
            
        self.prepare()

    def prepare(self):
        self.log(LogLevel.INFO, 'Prepare alfred sources packages...')
        self.create_symlink(UpdateUtils.ros_install_prefix, '../')
        #self.create_symlink(os.path.basename(__file__), '../../')
        
        os.chdir('../..')
        self.update_workspace()

    def update_workspace(self):
        self.log(LogLevel.INFO, 'Update workspace...')
        
        if os.path.isfile(UpdateUtils.setup_sh):
            self.shell_source(UpdateUtils.setup_sh)
        elif os.environ.get(UpdateUtils.env_ros_package_path) == None:
            self.log(LogLevel.ERROR, 'You must source java catkin setup.sh environment script')
            sys.exit()
        
        self.wstool()
        self.genjava()
        self.catkin_make()
        self.update_eclipse()

    def wstool(self):
        self.log(LogLevel.INFO, 'Execute wstool')
        
        files = os.listdir(UpdateUtils.alfred_full_path)
        for fn in files:
            if fn.endswith(UpdateUtils.ros_install_prefix) and fn != UpdateUtils.ros_install_prefix:
                wstool.wstool_cli.wstool_main(['wstool', 'merge', '-t', 'src', UpdateUtils.alfred_full_path + '/' + fn])
        
        wstool.wstool_cli.wstool_main(['wstool', 'update', '-t', 'src'])

    def genjava(self):
        self.log(LogLevel.INFO, 'Execute genjava_message_artifacts')
        args = ['genjava_message_artifacts', '-p'] + UpdateUtils.msg_packages;
        genjava.standalone_main(args)

    def catkin_make(self):
        self.log(LogLevel.INFO, 'Execute catkin_make')
        if subprocess.call(['catkin_make', '--directory', os.getcwd()]) != 0:
            self.log(LogLevel.ERROR, 'catkin_make failed, update aborted')
            sys.exit()

    def update_eclipse(self):
        self.log(LogLevel.INFO, 'Update eclipse projects files...')
        os.chdir('./src')

        path = os.getcwd()

        for fn in os.listdir('.'):
            dir = path + '/' + fn + '/'
            print (dir)
            if not os.path.isfile(dir) and os.path.isfile(dir + 'build.gradle'):
                os.chdir(dir)
                subprocess.call(['./gradlew', 'cleanEclipse', 'eclipse'])

    def is_in_alfred_full(self):
        result = os.getcwd().endswith(UpdateUtils.alfred_full_path)
        return result

    def is_in_workspace(self):
        result = False
        files = os.listdir(os.getcwd())
        for fn in files:
            if fn == 'src':
                result = True
                break
        return result
    
    def create_symlink(self, filename, destination):
        if os.path.isfile(destination + filename):
            self.log(LogLevel.WARNING, 'File %s already exists, skip' % (filename))
        else:
            os.symlink(os.getcwd() + '/' + filename, destination + filename)
            self.log(LogLevel.INFO, 'Symlink for %s created' % (filename))

    def shell_source(self, script):
        """Sometime you want to emulate the action of "source" in bash,
        settings some environment variables. Here is a way to do it."""
        import subprocess, os
        pipe = subprocess.Popen(". %s; env" % script, stdout=subprocess.PIPE, shell=True)
        output = pipe.communicate()[0]
        env = dict((line.split("=", 1) for line in output.splitlines()))
        os.environ.update(env)
    
    def log(self, level, message):
        print('%s%s\x1b[0m' % (level, message))

class LogLevel:
    DEBUG = '\x1b[0m'
    INFO = '\x1b[1;32m'
    WARNING = '\x1b[1;33m'
    ERROR = '\x1b[1;31m'
