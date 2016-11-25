import subprocess

def in_node():
  return 'cd node;'

def install():
  subprocess.getstatusoutput('sudo yum -y install gcc-c++ make openssl-devel git')
  subprocess.getstatusoutput('git clone git://github.com/nodejs/node.git')
  subprocess.getstatusoutput(in_node() + 'git checkout v6.9.1')
  subprocess.getstatusoutput(in_node() + './configure')
  subprocess.getstatusoutput(in_node() + 'make')
  subprocess.getstatusoutput(in_node() + 'sudo make install')

def main():
  install()