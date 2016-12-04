#!/usr/bin/python3
import subprocess, time, sys, logging
import logger, ui
import monitor

"""
Main method to start the program
"""

instance_ip = None
logger = logger.Logger()

def main():
  if len(sys.argv) == 2 and valid_ip_address(sys.argv[1]):
    global instance_ip
    instance_ip = '-'.join(sys.argv[1].split('.'))
    menu()
  else:
    logger.log('Cannot parse ip address', 'e')


"""
Menu level 2, after user has chosen the instance
"""


def menu():
  try:
    flag = True
    while (flag):
      option = ui.show('Please choose a task ',
                       ['Run a command', 'Check CPU'])
      if option == 0:
        # Run a command
        cmd = input('Enter command: ')
        ssh_exec(instance_ip, cmd)
      elif option == 1:
        # Check CPU
        monitor.get_cpu_usage(instance_ip)
      elif option == -99:
        flag = False
  except:
    logger.log(sys.exc_info()[0], 'e')
    logging.exception('EXCEPTION')


"""
A utility method to help executing a command on an instance over SSH, only the command is required i.e. no ssh prefix needed
Argument(s):
-ip address of the instance
-the command on the instance over SSH
"""


def ssh_exec(instance_ip, cmd):
  wait_ssh_port(instance_ip)  # make sure ssh port is open
  full_cmd = "ssh -t ubuntu@ec2-" + instance_ip + ".us-west-2.compute.amazonaws.com " + cmd
  logger.log(cmd, 'w')
  (status, output) = subprocess.getstatusoutput(full_cmd)
  logger.log(status, 'st')
  logger.log(output, 'o')
  return (status, output)

"""
Keep polling an instance to check if its SSH port is openned
Argument(s):
-instance ip address
"""


def wait_ssh_port(instance_ip):
  scan_ssh_port = "ssh -t ubuntu@ec2-" + instance_ip + ".us-west-2.compute.amazonaws.com " + 'nc -zv localhost 22'
  (status, output) = subprocess.getstatusoutput(scan_ssh_port)
  while status != 0:
    time.sleep(10)
    (status, output) = subprocess.getstatusoutput(scan_ssh_port)
  logger.log('SSH port is open', 's')


"""
Check if a string is a valid IP address
Argument(s):
-ip address string
Return:
-boolean
"""


def valid_ip_address(text):
  address = text.split('.')
  all_numbers = True
  for n in address:
    if not n.isdigit():
      all_numbers = False
  return len(address) == 4 and all_numbers


if __name__ == '__main__':
  main()
