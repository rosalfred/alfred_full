#!/usr/bin/env python

import os
import subprocess
import sys

class UpdateUtils:
    def __init__(self):
        self.data = []

    def init(self):
        # Check if current directory is alfred_full, in this case => init
        if self.is_in_alfred_full():
            self.prepare()
        # in this case we are in workspace
        elif self.is_in_workspace():
            self.update_workspace()
        # in this case => error
        else:
            self.log(LogLevel.ERROR, 'You are not in a ROS workspace. Exit.')
            sys.exit()

    def prepare(self):
        self.log(LogLevel.INFO, 'Prepare alfred sources packages...')
        self.create_symlink('.rosinstall', '../')
        self.create_symlink(os.path.basename(__file__), '../../')
            
        os.chdir('../..')
        self.update_workspace()

    def update_workspace(self):
        self.log(LogLevel.INFO, 'Update workspace...')
        
        if os.path.isfile('devel/setup.sh'):
            self.shell_source('devel/setup.sh')
        elif os.environ.get('ROS_PACKAGE_PATH') == None:
            self.log(LogLevel.ERROR, 'You must source java catkin setup.sh environment script')
            sys.exit()
        
        self.wstool()
        self.genjava()
        self.catkin_make()
        self.update_eclipse()

    def wstool(self):
        self.log(LogLevel.INFO, 'Execute wstool')
        
        files = os.listdir('src/alfred_full/')
        for fn in files:
            if fn.endswith('.rosinstall') and fn != '.rosinstall':
                subprocess.call(['wstool', 'merge', '-t', 'src', './src/alfred_full/' + fn])
                
        subprocess.call(['wstool', 'update', '-t', 'src'])

    def genjava(self):
        self.log(LogLevel.INFO, 'Execute genjava_message_artifacts')
        subprocess.call(['genjava_message_artifacts', '-p', 'rosbuilding_msgs', 'media_msgs', 'heater_msgs'])

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
        result = os.getcwd().endswith('src/alfred_full')
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
