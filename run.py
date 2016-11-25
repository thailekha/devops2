#!/usr/bin/python3
import boto
import boto.ec2
import subprocess
import time
import logger
import ui
import dev_util
import sys
import logging

"""
Author: Thai Kha Le
This is the main script to run the project. It should be executed and given 3 command-line arguments specifying
respectively the ami, the key name and the directory of the pem file. Also, the check_webserver.py should also be in
the same folder

There are some utility methods in this script that should be left in dev_util module. However, they are kept here
because they need the pem directory
"""

logger = logger.Logger()
# ./run.py ami-7172b611 thaikhale ./thaikhale.pem
# default arguments to create instane
ami = 'ami-7172b611'
key_name = 'thaikhale'
pem_dir = './thaikhale.pem'

"""
Main method to start the program
"""


def main():
  # firslty, try parsing the command-line arguments for the ami, key name and directory of the pem file to be used later to create instance
  parse_instance_args()
  dev_util.sync_time()
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
The main menu to let user choose either to make a new instance or to choose an existing and running instance
"""


def menu_level_1():
  flag = True
  while (flag):
    run_mode = ui.show('~~~Level 1 - Welcome, please choose an option ',
                       ['Create new instance', 'Connect to the most recent instance', 'Choose from running instances'])
    if run_mode == 0:
      # Create new instance
      menu_level_2()
    elif run_mode == 1:
      # Connect to the most recent instance
      conn = boto.ec2.connect_to_region('us-west-2')
      newest_instance = dev_util.find_newest_instance(conn)
      if newest_instance != None:
        menu_level_2(conn, newest_instance)
    elif run_mode == 2:
      # Choose from running instances
      conn = boto.ec2.connect_to_region('us-west-2')
      (instances, names) = dev_util.get_all_instances(conn)
      if len(instances) == 0:
        logger.log('No running instance found', 'w')
      else:
        index = ui.show('~~~Level 1a - Please choose an instance ', names)
        if index >= 0 and index < len(instances):
          chosen_instance = instances[index]
          logger.log('Chose ' + chosen_instance.tags['Name'], 'st')
          menu_level_2(conn, chosen_instance)
    elif run_mode == -99:
      flag = False


"""
Menu level 2, after user has chosen the instance
"""


def menu_level_2(conn=None, instance=None):
  try:
    if conn == None and instance == None:
      (conn, instance) = create()
      logger.log('New instance created, ' + instance.tags['Name'], 's')
    elif conn != None and instance != None:
      logger.log('Connected to instance, ' + instance.tags['Name'], 's')
    else:
      logger.log('Error: invalid conn or instance', 'e')
      sys.exit(2)

    flag = True
    while (flag):
      option = ui.show('~~~Level 2 - Please choose a task ',
                       ['Print SSH command to connect to the instance', 'Run a command', 'Copy file to instance',
                        'Check CPU',
                        'Manage Nginx', 'Terminate'])
      if option == 0:
        # Print SSH command to connect to the instance
        logger.log('ssh -i "' + pem_dir + '" ec2-user@' + dev_util.get_ip(instance), 's')
      elif option == 1:
        # Run a command
        cmd = input('Enter command: ')
        ssh_exec(dev_util.get_ip(instance), cmd)
      elif option == 2:
        # Copy file to instance
        file_dir = input('Enter file directory (no quotes needed):')
        scp_exec(dev_util.get_ip(instance), file_dir)
      elif option == 3:
        # Check CPU
        result = monitor_cpu(dev_util.get_ip(instance))
        if result != None and result:
          create(conn)
      elif option == 4:
        # Manage Nginx
        manage_nginx(dev_util.get_ip(instance))
      elif option == 5:
        #change name
        instance.remove_tag('Name', instance.tags['Name'])
        instance.update()
        instance.add_tag('Name',input('New name ===> '))
        instance.update()
      elif option == 6:
        # Terminate
        terminate(conn, instance)
        flag = False
      elif option == -99:
        flag = False
  except:
    logger.log(sys.exc_info()[0], 'e')
    logging.exception('EXCEPTION')


"""
The menu to let user choose tasks related to managing nginx (Menu level 3)
"""


def manage_nginx(instance_ip):
  (status, output) = ssh_exec(instance_ip, 'sudo cat /var/log/nginx/access.log')

  if status == 0:
    lines = output.split('\n')[
            :-1]  # list of lines extracted from output, except the last one i.e. "Connection to ... closed"
    logger.log(lines, 'w')
    flag = True
    while flag:
      user_choice = ui.show('~~~Level 3 - Nginx manager - please choose an option',
                            ['Print all unique IP addresses that has made requests', 'Print logs from an IP address',
                             'Print recent access logs', 'Update'])
      if user_choice == 0:
        # Print all unique IP addresses that has made requests
        ip_addresses = set()
        for l in lines:
          n_ip = l.split('-')[0].strip()
          if dev_util.valid_ip_address(n_ip):
            ip_addresses.add(n_ip)
        for ip in list(ip_addresses):
          logger.log(ip, 'st')
      elif user_choice == 1:
        # Print logs from an IP address
        query = input('IP address: ')
        if dev_util.valid_ip_address(query):
          for l in lines:
            if query in l:
              logger.log(l, 'st')
      elif user_choice == 2:
        # Print recent access logs
        if len(lines) < 5:
          for l in lines:
            logger.log(l, 'st')
        else:
          for l in lines[-5:]:
            logger.log(l, 'st')
      elif user_choice == 3:
        # Update
        (status, output) = ssh_exec(instance_ip, 'sudo cat /var/log/nginx/access.log')
        lines = output.split('\n')[
                :-1]  # list of lines extracted from output, except the last one i.e. "Connection to ... closed"
      elif user_choice == -99:
        flag = False;


"""
A submenu prompting user to create another when CPU usage is above 50%
Argument(s):
-ip address of the instance
Returns
-Booean indicating whether user wants to create another instance or None
"""


def monitor_cpu(instance_ip):
  cpu_usage = dev_util.get_cpu_usage(instance_ip)
  if cpu_usage != None and cpu_usage > 50:
    logger.log('CPU usage is above 50%, do you want a new instance? [y/n]')
    return input('===>') == 'y'
  return None


"""
Terminate an instance and close the connection
Argument(s):
-Connection and instance objects
"""


def terminate(conn, instance):
  logger.log('Terminating instance', 'w')
  conn.terminate_instances(instance.id)
  conn.close()
  # conn.delete_security_group('httpssh3')


"""
Create an instance with a security group called httpssh3 allowing only HTTP and SSH connection
Argument(s):
-Connection object (default None)
-Boolean indicating whether to close the connection after creating an instance
"""


def create(conn=None, closeConn=False, testing=False):
  if conn == None:
    conn = boto.ec2.connect_to_region('us-west-2')
  httpssh3_available = False
  for s in conn.get_all_security_groups():
    if s.name == 'httpssh3':
      httpssh3_available = True
      break
  if not httpssh3_available:
    secgroup = conn.create_security_group('httpssh3', 'Only HTTP and SSH')
    secgroup.authorize('tcp', 80, 80, '0.0.0.0/0')  # HTTP
    secgroup.authorize('tcp', 22, 22, '0.0.0.0/0')  # SSH
  reservation = conn.run_instances(ami, key_name=key_name, instance_type='t2.micro', security_groups=['httpssh3'])
  logger.log(reservation.instances)
  instance = reservation.instances[0]
  instance.add_tag('Name', dev_util.get_instance_name())
  instance.update()

  dev_util.wait_running_state(instance)

  if not testing:
    dev_util.deploy_default_config(dev_util.get_ip(instance))  # install python, nginx, and run nginx

  if (closeConn):
    conn.close()
  return (conn, instance)


"""
Check if a program/service is installed, if not, install it
Argument(s):
-ip address of the instance
- the program name to install on the instance
"""


def do_install(instance_ip, program):
  (status, output) = ssh_exec(instance_ip, 'sudo yum -y list installed | grep ' + program)
  if status != 0:
    (status_install, output_install) = ssh_exec(instance_ip, 'sudo yum -y install ' + program)
    logger.log(status_install, 'st')
    logger.log(output_install, 'o')
  logger.log(program + ' installed', 's')


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


if __name__ == '__main__':
  main()
