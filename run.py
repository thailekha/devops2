#!/usr/bin/python3
import subprocess, time, sys, logging, boto3.ec2.cloudwatch
import util,monitor

"""
Main method to start the program
"""

instance_ip = None
logger = util.Logger()

def main():
  if len(sys.argv) == 2 and util.valid_ip_address(sys.argv[1]):
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
      option = util.ui.show('Please choose a task ',
                       ['Run a command', 'Check CPU','Cloudwatch metrics'])
      if option == 0:
        # Run a command
        cmd = input('Enter command: ')
        util.ssh_exec(instance_ip, cmd)
      elif option == 1:
        # Check CPU
        monitor.get_cpu_usage(instance_ip)
      elif option == 2:
        pass
      elif option == -99:
        flag = False
  except:
    logger.log(sys.exc_info()[0], 'e')
    logging.exception('EXCEPTION')


if __name__ == '__main__':
  main()
