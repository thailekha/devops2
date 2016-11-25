#!/usr/bin/python3
import logger
import subprocess
import run
import time
import boto
from datetime import datetime

"""
This module contains utility methods that the main script i.e. run can use
"""

logger = logger.Logger()

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
Generate a name to be used for an EC2 instance, the name is followed by the time string at the time
Return:
-A name string
"""


def get_instance_name():
  current = datetime.today()
  return 'My second API instance ' + str(current.day) + '/' + str(current.month) + '~' + str(current.hour) + ':' + str(
    current.minute) + ':' + str(current.second)


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
Keep polling an instance's state until getting the "running" state
Argument(s):
-instance object
"""


def wait_running_state(instance):
  state = instance.state
  while state != 'running':
    logger.log(state)
    time.sleep(10)
    instance.update()
    state = instance.state


"""
Check if python, nginx are installed, if not, install them and make sure nginx is running
Arguments:
-Ip address of the instance
"""


def deploy_default_config(instance_ip):
  run.do_install(instance_ip, 'python35')
  run.scp_exec(instance_ip, './install_node.py')
  run.scp_exec(instance_ip, './install_npm.py')
  #run.do_install(instance_ip, 'nginx')
  #run.scp_exec(instance_ip, './check_webserver.py')  # copy check_webserver.py to instance
  #run.ssh_exec(instance_ip, './check_webserver.py')  # execute the script
  #run.ssh_exec(instance_ip, './check_webserver.py')  # execute the script again to make sure nginx is running


"""
Find the most recent runnning instance
Argument(s):
-connection object
Return:
-The newest instance or None
"""


def find_newest_instance(conn):
  reservations = conn.get_all_reservations()
  newest_instance = None
  for r in reservations:
    for i in r.instances:
      if not hasattr(i, 'launch_time'):
        logger.log('Error, instance does not have launch_time attribute', 'e')
      if i.state == 'running' and 'Name' in list(i.tags) and (
            newest_instance == None or parse_ec2_time(i.launch_time) > parse_ec2_time(newest_instance.launch_time)):
        newest_instance = i
  if newest_instance == None:
    logger.log('Cannot find newest instance', 'e')
  else:
    logger.log('Found newest isntance', 's')
    logger.log(newest_instance.tags['Name'], 's')
    logger.log(newest_instance.launch_time, 's')
    logger.log(newest_instance.state, 's')
  return newest_instance


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


"""
Get the CPU usage of the currently connected instance
Argument(s):
-ip address of the instance
Returns
-CPU percentage in float or None
"""


def get_cpu_usage(instance_ip):
  (status, output) = run.ssh_exec(instance_ip,
                                  'top -n2 | grep Cpu | grep -v grep | tail -n 1 | awk \'{print $2}\' | grep -v PID')
  if status == 0:
    # format: connection to ... closed.\n ...%us
    cpu_usage_str = output.split('\n')[1].split('%')[0]
    logger.log('CPU usage: ' + cpu_usage_str + '%', 's')
    cpu_usage = float(cpu_usage_str)
    return cpu_usage
  else:
    logger.log('Error, please try again', 'e')
    return None


"""
Below this point are the preparation methods for the unittest methods above. Doing this separates boto from unittest to reduce overhead. Only needed values are achieved for testing instead of using boto.ec2 instance directly
"""

"""
Prepare for the test create instance method. It contains these steps:
-Gather a list of reservations
-Create a new in stance
-Gather a new list of reservations
-Find the created instance
-Get necessary values and terminate the instance
The values that are returned:
-Length of the old reservations list
-Length of the new reservations list
-Name of instance
-Length of the security groups list of instance
-The security group name
-State of instance (should be 'running')
-Type of instance i.e. t2.micro
"""


def test_create_instance_util():
  logger.log('Running create instance test', 'w')

  # size, name, secgroup, key, type
  logger.log('Gathering current reservations and instances', 'w')
  old_conn = boto.ec2.connect_to_region('us-west-2')
  old_reservations = old_conn.get_all_reservations()
  old_conn.close()
  logger.log('Creating new instance', 'w')
  run.create(testing=True)
  logger.log('Gathering new reservations and instances', 'w')
  new_conn = boto.ec2.connect_to_region('us-west-2')
  new_reservations = new_conn.get_all_reservations()

  # Find the most recent one
  logger.log('Finding the created instance', 'w')
  created_instance = find_newest_instance(new_conn)

  # get all values to be tested
  len_old_rv = len(old_reservations)
  len_new_rv = len(new_reservations)
  name = created_instance.tags['Name']
  len_sec_groups = len(created_instance.groups)
  sec_group_name = created_instance.groups[0].name
  state = created_instance.state
  inst_type = created_instance.instance_type

  run.terminate(new_conn, created_instance)

  return (len_old_rv, len_new_rv, name, len_sec_groups, sec_group_name, state, inst_type)


"""
Prepare for the test get ip address method. It contains these steps:
-Create an instance
-Get its ip address
-Terminate  it and return the ip address
"""


def test_get_ip_address_util():
  (conn, instance) = run.create(testing=True)
  ip_addr = get_ip(instance)
  run.terminate(conn, instance)
  return ip_addr


"""
Prepare for the test copy check webserver script method. It contains these steps:
-Create an instance
-Copy the check_webserver.py to it
-Terminate  it and return the status of subprocess
"""


def test_copy_web_checkserver_script_util():
  (conn, instance) = run.create(testing=True)
  run.scp_exec(get_ip(instance), './check_webserver.py')
  (status, output) = run.ssh_exec(get_ip(instance), 'ls | grep check_webserver.py')
  run.terminate(conn, instance)
  return status


"""
Prepare for the test install program/service method. It contains these steps:
-Create an instance
-Install a program called "stress"
-Terminate  it and return the status of subprocess
"""


def test_do_install_util():
  (conn, instance) = run.create(testing=True)
  run.do_install(get_ip(instance), 'stress')
  (status, output) = run.ssh_exec(get_ip(instance), 'sudo yum -y list installed | grep stress')
  run.terminate(conn, instance)
  return status


if __name__ == '__main__':
  print('This is a utility module')
