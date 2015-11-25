#!/usr/bin/env python

import os
import subprocess
import sys

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
        self.create_symlink(os.path.basename(__file__), '../../')
        
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
                subprocess.call(['wstool', 'merge', '-t', 'src', UpdateUtils.alfred_full_path + '/' + fn])
                
        subprocess.call(['wstool', 'update', '-t', 'src'])

    def genjava(self):
        self.log(LogLevel.INFO, 'Execute genjava_message_artifacts')
        args = ['genjava_message_artifacts', '-p'] + UpdateUtils.msg_packages;
        subprocess.call(args)

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

if __name__ == '__main__':
    UpdateUtils().init()
