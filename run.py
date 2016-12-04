#!/usr/bin/python3
import boto, boto.ec2, subprocess, time, datetime, sys, logging
import logger, ui
import monitor

"""
Author: Thai Kha Le
This is the main script to run the project. It should be executed and given 3 command-line arguments specifying
respectively the ami, the key name and the directory of the pem file.

There are some utility methods in this script that should be left in dev_util module. However, they are kept here
because they need the pem directory
"""

logger = logger.Logger()
ami = 'ami-7172b611'
key_name = 'thaikhale'
pem_dir = './thaikhale.pem'

"""
Main method to start the program
"""


def main():
  # firslty, try parsing the command-line arguments for the ami, key name and directory of the pem file to be used later to create instance
  parse_instance_args()
  sync_time()
  menu_level_1()


"""
Parse the command-line arguments for the ami, key name and directory of the pem file to be used later to create instance
"""


def parse_instance_args():
  if len(sys.argv) == 4 and len(sys.argv[1].split('-')) == 2 and sys.argv[1].split('-')[0] == 'ami' and '.pem' in \
    sys.argv[3].split('/').pop():
    ami = sys.argv[1]
    key_name = sys.argv[2]
    pem_dir = sys.argv[3]
    logger.log('Successfully parsed command line arguments: ', 'st')
    logger.log('ami: ' + ami, 's')
    logger.log('key name: ' + key_name, 's')
    logger.log('pem directory: ' + pem_dir, 's')
  else:
    logger.log('Failed to parse command line arguments, using default values', 'e')


"""
Let user choose which instance to connect to
"""


def menu_level_1():
  flag = True
  while (flag):
    # Choose from running instances
    conn = boto.ec2.connect_to_region('us-west-2')
    (instances, names) = get_all_instances(conn)
    if len(instances) == 0:
      logger.log('No running instance found', 'w')
      flag = False
    else:
      index = ui.show('~~~Level 1a - Please choose an instance ', names)
      if index >= 0 and index < len(instances):
        chosen_instance = instances[index]
        logger.log('Chose ' + chosen_instance.tags['Name'], 'st')
        menu_level_2(conn, chosen_instance)
      elif index == -99:
        flag = False


"""
Menu level 2, after user has chosen the instance
"""


def menu_level_2(conn=None, instance=None):
  try:
    if conn == None and instance == None:
      return;
    elif conn != None and instance != None:
      logger.log('Connected to instance, ' + instance.tags['Name'], 's')
    else:
      logger.log('Error: invalid conn or instance', 'e')
      sys.exit(2)

    flag = True
    while (flag):
      option = ui.show('~~~Level 2 - Please choose a task ',
                       ['Run a command', 'Copy file to instance',
                        'Check CPU', 'Change name'])
      if option == 0:
        # Run a command
        cmd = input('Enter command: ')
        ssh_exec(get_ip(instance), cmd)
      elif option == 1:
        # Copy file to instance
        file_dir = input('Enter file directory (no quotes needed):')
        scp_exec(get_ip(instance), file_dir)
      elif option == 2:
        # Check CPU
        monitor.get_cpu_usage(get_ip(instance))
      elif option == 3:
        # change name
        instance.remove_tag('Name', instance.tags['Name'])
        instance.update()
        instance.add_tag('Name', input('New name ===> '))
        instance.update()
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
  full_cmd = "ssh -t -o StrictHostKeyChecking=no -i '" + pem_dir + "' ec2-user@" + instance_ip + " " + cmd
  logger.log(cmd, 'w')
  (status, output) = subprocess.getstatusoutput(full_cmd)
  logger.log(status, 'st')
  logger.log(output, 'o')
  return (status, output)


"""
Execute scp command i.e. copy a file onto the instance, only the directory of the file is needed
Argument(s):
-ip address of the instance
-the directory of the file to bo copied to the instance
"""


def scp_exec(instance_ip, file_dir):
  # logger.log('Copying file to ec2')
  wait_ssh_port(instance_ip)  # make sure ssh port is open
  (status, output) = subprocess.getstatusoutput(
    'scp -i "' + pem_dir + '" "' + file_dir.replace('"', '') + '" ec2-user@' + instance_ip + ':.')
  logger.log(status, 'st')
  logger.log(output, 'o')
  # make the file readable
  if status == 0:
    ssh_exec(instance_ip, 'chmod +x ' + file_dir.split('/').pop())


"""
Keep polling an instance to check if its SSH port is openned
Argument(s):
-instance ip address
"""


def wait_ssh_port(instance_ip):
  scan_ssh_port = "ssh -t -o StrictHostKeyChecking=no -i '" + pem_dir + "' ec2-user@" + instance_ip + " " + 'nc -zv localhost 22'
  (status, output) = subprocess.getstatusoutput(scan_ssh_port)
  while status != 0:
    time.sleep(10)
    (status, output) = subprocess.getstatusoutput(scan_ssh_port)
  logger.log('SSH port is open', 's')


"""
Synchronize the time of the local machine with the ubuntu server
"""


def sync_time():
  logger.log('Synchronizing time ...')
  (status, output) = subprocess.getstatusoutput('sudo ntpdate ntp.ubuntu.com')
  logger.log(status, 'st')
  logger.log(output, 'o')


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


"""
Parse the time string of an EC2 istance to a datetime object
Argument(s):
-time string
Return:
-datetime object
"""


def parse_ec2_time(time_str):
  return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')


"""
Keep polling an instance to get its ip address
Argument(s):
-instance object
Return:
-ip address of the instance
"""


def get_ip(instance):
  instance.update()
  instance_ip = instance.ip_address
  # string format and separated by .
  while type(instance_ip) != type("") and len(instance_ip.split(".")) != 4:
    time.sleep(5)
    instance_ip = instance.ip_address
  return instance_ip


"""
Retrieve all running instances
Argument(s):
-connection object
Return:
-a tuple of list of instances an list of names of those
"""


def get_all_instances(conn):
  reservations = conn.get_all_reservations()
  instances = []
  names = []
  for r in reservations:
    for i in r.instances:
      # only collect running instances
      if i.state == 'running' and 'Name' in list(i.tags):
        instances.append(i)
        names.append(i.tags['Name'])
  return (instances, names)


if __name__ == '__main__':
  main()
