import subprocess

def install():
  subprocess.getstatusoutput('git clone git://github.com/isaacs/npm.git')
  subprocess.getstatusoutput('cd npm;sudo make install')

def main():
  install()