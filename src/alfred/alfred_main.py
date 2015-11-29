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
import sys
import tempfile
import shutil

import catkin_pkg.packages
import genjava
import wstool.wstool_cli
import rosjava_build_tools

ROSINSTALL_PREFIX = '.rosinstall'
ALFREDFULL_PATH = 'src/alfred_full'

def standalone_parse_arguments(argv):
    parser = argparse.ArgumentParser(description='Update Alfred ROS packages from repository, build catkin and update eclipse project.')
    parser.add_argument('-p', '--package', action='store', nargs='*', default=[], help='a list of packages to update')
    parser.add_argument('-w', '--wstool', default=False, action='store_true', help='run wstool update')
    parser.add_argument('-g', '--genmsgs', default=False, action='store_true', help='run generate_message_artifacts')
    parser.add_argument('-c', '--catkin', default=False, action='store_true', help='run catkin_make')
    parser.add_argument('-e', '--eclipse', default=False, action='store_true', help='update Eclipse project')
    parser.add_argument('--reset', default=False, action='store_true', help='reset ROS workspace')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='enable verbosity in debugging')
    parser.add_argument('-l', '--list', default=False, action='store_true', help='list the packages it would update')
    parsed_arguments = parser.parse_args(argv)
    return parsed_arguments

def standalone_main(argv):
    options = standalone_parse_arguments(argv[1:])
    Util.log_verbose = options.verbose
    UpdateUtils(options).run()
        
class UpdateUtils(object):

    def __init__(self, options):
        self.options = options
        self.depends = None
    
    def run(self):
        if self.options.reset:
            self.reset_workspace()
            sys.exit()
        
        if self.options.package:
            self.depends = []
        
        if self.options.list or self.options.package:
            self.load_packages()
        
        if self.options.list:
            self.list_packages()
            sys.exit()
        
        self.prepare()
        self.update_workspace()

    def prepare(self):
        '''
        Prepare workspace, create .rosinstall file in src dir
        '''
        
        Util.log(LogLevel.INFO, 'Prepare alfred sources packages...')
        Util.create_symlink(os.getcwd() + '/' + ALFREDFULL_PATH + "/", os.getcwd() + '/src/', ROSINSTALL_PREFIX)

    def update_workspace(self):
        '''
        Run all needed actions for current workspace: update wstool, update genjava, run catkin, update Eclipse projects
        '''
        
        Util.log(LogLevel.INFO, 'Update workspace...')
        
        '''If all options are false do all jobs'''
        do_all = not (self.options.wstool or self.options.genmsgs or self.options.catkin or self.options.eclipse)
        
        if do_all or self.options.wstool:
            self.wstool()
            
        if do_all or self.options.genmsgs:
            self.genjava()
        
        if do_all or self.options.catkin:
            self.catkin()
        
        if do_all or self.options.eclipse:
            self.update_eclipse()

    def wstool(self):
        '''
        Merge all *.rosintall files in alfred_full package within the src/.rosinstall
        Execute wstool update
        '''
        
        Util.log(LogLevel.INFO, 'Execute wstool')
        
        files = os.listdir(ALFREDFULL_PATH)
        for fn in files:
            if fn.endswith(ROSINSTALL_PREFIX) and fn != ROSINSTALL_PREFIX:
                wstool.wstool_cli.wstool_main(['wstool', 'merge', '-t', 'src', ALFREDFULL_PATH + '/' + fn])
        
        wstool.wstool_cli.wstool_main(['wstool', 'update', '-t', 'src'])

    def genjava(self):
        '''
        Run generate_message_artifacts for all packages messages contains in the workspace
        '''
        
        Util.log(LogLevel.INFO, 'Execute genjava_message_artifacts')
        
        msg_packages = []
        current_path = os.getcwd()
        
        sorted_package_tuples = rosjava_build_tools.catkin.index_message_package_dependencies_from_local_environment(package_name_list=[])
        
        for unused_relative_path, package in sorted_package_tuples:
            if package.filename.startswith(current_path):
                msg_packages += [unused_relative_path]
                
        args = ['genjava_message_artifacts', '-p'] + msg_packages;
        genjava.standalone_main(args)

    def catkin(self):
        '''
        Prepare catkin_make args and run it on the workspace
        '''
        
        packages = None
        
        if self.depends:
            packages = []
            
            for package in self.depends:
                packages += [package.name]
            
        self.catkin_make(packages)
                
    def catkin_make(self, packages = None):
        '''
        Run catkin_make
        :param packages: list of packages to build, if None, all packages will be build
        '''
        
        Util.log(LogLevel.INFO, 'Execute catkin_make')
        args = ['catkin_make', '--directory', os.getcwd()]
        
        if packages:
            args = args + ['--pkg'] + packages
        
        if subprocess.call(args) != 0:
            Util.log(LogLevel.ERROR, 'catkin_make failed, update aborted')
            sys.exit()

    def update_eclipse(self):
        '''
        Update all Eclipse projects files.
        If gradle 'eclipse' plugin was not enable for the package, create a default eclipse project.
        '''
        
        Util.log(LogLevel.INFO, 'Update eclipse projects files...')
        os.chdir('./src')

        path = os.getcwd()

        for fn in os.listdir('.'):
            dir = path + '/' + fn + '/'
            
            if not os.path.isfile(dir) and os.path.isfile(dir + 'package.xml'):
                if os.path.isfile(dir + 'build.gradle') and 'eclipse' in open(dir + 'build.gradle').read():
                    os.chdir(dir)
                    subprocess.call(['./gradlew', 'cleanEclipse', 'eclipse'])
                else:
                    if not os.path.isfile(dir + '.project'): #TODO need to update existing file ?
                        Util.log(LogLevel.INFO, 'Create default project file for %s' % fn)
                        shutil.copyfile(path + '/alfred_full/src/templates/template.project', dir + '.project')
                        Util.replace(dir + '.project', '${package_name}', fn) #TODO replace by real package name instead of fn
    
    def load_packages(self):
        '''
        Load all packages contain in the workspace
        '''
        
        self.packages = catkin_pkg.packages.find_packages('./src')
        
        if self.options.package:
            for package in self.options.package:
                if package in self.packages:
                    self.depends += [self.packages[package]]
            
            for package in self.options.package:
                self.load_depends(package)
        
    def load_depends(self, package):
        '''
        Load all packages dependencies for a specific package
        :param package: The package to check
        '''
        
        if package in self.packages:
            package = self.packages[package]
            
            if not package in self.depends:
                self.depends = [package] + self.depends
            
            for p in package['build_depends']:
                self.load_depends(p.name)
        
    def list_packages(self):
        for package in self.packages:
            self.list_package(package)
    
    def list_package(self, package, level = 0):
        '''
        List all packages recursively
        :param package: Name of the package to list
        :param level: Recursive level
        '''
        
        hasPackage = package in self.packages
        hasDependencies = False
        deps = {}
        
        if hasPackage:
            package = self.packages[package].name
            deps = self.packages[package]['build_depends']
            hasDependencies = bool(deps)
        
        prefix = '+---'
        if hasPackage and hasDependencies:
            prefix = '\---'
        
        for num in range(0, level):
            prefix = '     ' + prefix
        
        print('{0} {1}'.format(prefix, package))
        
        if hasDependencies:
            for p in deps:
                self.list_package(p.name, level + 1)
    
    def reset_workspace(self):
        '''
        Reset the ROS workspace. Delete 'devel' and 'build' folder and rebuild 'alfred_full' package
        '''
        
        if os.path.isdir('devel'):
            Util.log(LogLevel.INFO, 'Clean ROS workspace...')
            
            if not Util.remove_dir('devel') or not Util.remove_dir('build'):
                return
            
            Util.log(LogLevel.INFO, 'Rebuild alfred_full package')
            self.catkin_make(['alfred_full'])

class Util:
    log_verbose = False
    
    @staticmethod
    def create_symlink(source_dir, destination_dir, filename):
        '''
        Create a symlink
        :param source_dir: The directory wich contains the source file
        :param destination_dir: The directory where the symlink will be created
        :param filename: The name of the target file
        '''
        
        if os.path.isfile(destination_dir + filename):
            Util.log(LogLevel.WARNING, 'File %s already exists, skip' % (filename))
        else:
            os.symlink(source_dir + filename, destination_dir + filename)
            Util.log(LogLevel.INFO, 'Symlink for %s created' % (filename))
    
    @staticmethod
    def remove_dir(dirname):
        '''
        Remove a folder recursively
        :param dirname: Path of the folder to remove
        '''
        
        result = False
        log_message = None
        log_level = LogLevel.INFO
        
        if os.path.isdir(dirname):
            shutil.rmtree(dirname)
            
            if not os.path.isdir(dirname):
                log_message = 'Directory \'%s\' was removed successfuly' % dirname
                result = True
            else:
                log_message = 'Directory \'%s\' can\'t be removed' % dirname
                log_level = LogLevel.ERROR
            
        else:
            log_message = '%s is not a directory' % dirname
            
        Util.log(log_level, log_message)
        
        return result
    
    @staticmethod
    def replace(source_file_path, target, replacement):
        '''
        Replace a string in a file
        :param source_file_path: File to work with it
        :param target: The string to be replaced
        :param replacement: The replacement string
        '''
        
        fh, target_file_path = tempfile.mkstemp()
        
        with open(target_file_path, 'w') as target_file:
            with open(source_file_path, 'r') as source_file:
                for line in source_file:
                    target_file.write(line.replace(target, replacement))
        
        os.remove(source_file_path)
        shutil.move(target_file_path, source_file_path)
    
    @staticmethod
    def log(level, message):
        '''
        Print a message to stdout
        :param level: Level of the message to print (see LogLevel)
        :param message: Message to print
        '''
        
        if level != LogLevel.DEBUG or Util.log_verbose:
            print('%s%s\x1b[0m' % (level, message))
    
class LogLevel:
    DEBUG = '\x1b[0m'
    INFO = '\x1b[1;32m'
    WARNING = '\x1b[1;33m'
    ERROR = '\x1b[1;31m'
