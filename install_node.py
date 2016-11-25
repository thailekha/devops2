#!/usr/bin/python3

import subprocess


def in_node():
  return 'cd node;'


def install():
  (s1, o1) = subprocess.getstatusoutput('sudo yum -y install gcc-c++ make openssl-devel git')
  print(s1)
  print(o1)
  (s2, o2) = subprocess.getstatusoutput('git clone git://github.com/nodejs/node.git')
  print(s2)
  print(o2)
  (s3, o3) = subprocess.getstatusoutput(in_node() + 'git checkout v6.9.1')
  print(s3)
  print(o3)
  (s4, o4) = subprocess.getstatusoutput(in_node() + './configure')
  print(s4)
  print(o4)
  (s5, o5) = subprocess.getstatusoutput(in_node() + 'make')
  print(s5)
  print(o5)
  (s6, o6) = subprocess.getstatusoutput(in_node() + 'sudo make install')
  print(s6)
  print(o6)

if __name__ == '__main__':
  install()