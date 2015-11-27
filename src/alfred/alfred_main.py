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

import rosjava_build_tools

def standalone_parse_arguments(argv):
    parser = argparse.ArgumentParser(description='Update Alfred ROS packages from repository, build catkin and update eclipse project.')
    #parser.add_argument('-p', '--package', action='store', nargs='*', default=[], help='a list of packages to update [WIP]')
    parser.add_argument('-w', '--wstool', default=False, action='store_true', help='run wstool update [WIP]')
    parser.add_argument('-g', '--genmsgs', default=False, action='store_true', help='run generate_message_artifacts')
    parser.add_argument('-c', '--catkin', default=False, action='store_true', help='run catkin_make')
    parser.add_argument('-e', '--eclipse', default=False, action='store_true', help='update Eclipse project')
    #parser.add_argument('-v', '--verbose', default=False, action='store_true', help='enable verbosity in debugging')
    #parser.add_argument('-l', '--list', default=False, action='store_true', help='list the packages it would update')
    parsed_arguments = parser.parse_args(argv)
    return parsed_arguments

def standalone_main(argv):
    options = standalone_parse_arguments(argv[1:])
    UpdateUtils(options).init()
        
class UpdateUtils(object):
    ros_install_prefix = '.rosinstall'
    alfred_full_path = 'src/alfred_full'

    def __init__(self, options):
        self.options = options
    
    def init(self):
        is_in_workspace = self.is_in_workspace() # in this case we are in workspace
        is_in_alfred_full = self.is_in_alfred_full() # if current directory is alfred_full
            
        self.prepare()
        self.update_workspace()

    def prepare(self):
        self.log(LogLevel.INFO, 'Prepare alfred sources packages...')
        self.create_symlink(os.getcwd() + '/' + UpdateUtils.alfred_full_path + "/", os.getcwd() + '/src/', UpdateUtils.ros_install_prefix)

    def update_workspace(self):
        self.log(LogLevel.INFO, 'Update workspace...')
        
        '''If all options are false do all jobs'''
        do_all = not (self.options.wstool or self.options.genmsgs or self.options.catkin or self.options.eclipse)
        
        if do_all or self.options.wstool:
            self.wstool()
            
        if do_all or self.options.genmsgs:
            self.genjava()
        
        if do_all or self.options.catkin:
            self.catkin_make()
        
        if do_all or self.options.eclipse:
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
        
        msg_packages = []
        current_path = os.getcwd()
        
        sorted_package_tuples = rosjava_build_tools.catkin.index_message_package_dependencies_from_local_environment(package_name_list=[])
        
        for unused_relative_path, package in sorted_package_tuples:
            if package.filename.startswith(current_path):
                msg_packages += [unused_relative_path]
                
        args = ['genjava_message_artifacts', '-p'] + msg_packages;
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
    
    def create_symlink(self, source_dir, destination_dir, filename):
        print(source_dir)
        print(destination_dir)
        print(filename)
        if os.path.isfile(destination_dir + filename):
            self.log(LogLevel.WARNING, 'File %s already exists, skip' % (filename))
        else:
            os.symlink(source_dir + filename, destination_dir + filename)
            self.log(LogLevel.INFO, 'Symlink for %s created' % (filename))
    
    def log(self, level, message):
        print('%s%s\x1b[0m' % (level, message))

class LogLevel:
    DEBUG = '\x1b[0m'
    INFO = '\x1b[1;32m'
    WARNING = '\x1b[1;33m'
    ERROR = '\x1b[1;31m'
