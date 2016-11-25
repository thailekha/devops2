#!/usr/bin/python3
import unittest
import logger
import dev_util

logger = logger.Logger()


class MyTest(unittest.TestCase):
  """
    The values that are asserted:
  -Length of the old reservations list
  -Length of the new reservations list
  -Name of instance
  -Length of the security groups list of instance
  -The security group name
  -State of instance (should be 'running')
  -Type of instance i.e. t2.micro
  """

  def test_create_instance(self):
    (len_old_rv, len_new_rv, name, len_sec_groups, sec_group_name, state,
     inst_type) = dev_util.test_create_instance_util()
    logger.log('Executing assertion tests', 'w')
    self.assertEqual(len_old_rv + 1, len_new_rv)
    self.assertEqual(name[:22], 'My second API instance')
    self.assertEqual(len_sec_groups, 1)  # security groups
    self.assertEqual(sec_group_name, 'httpssh3')
    self.assertEqual(state, 'running')
    self.assertEqual(inst_type, 't2.micro')

  """
  The values that are asserted:
  -Type of the ip address string
  -The IP address should be separated by '.' to 4 parts
  """

  def test_get_ip_address(self):
    ip_addr = dev_util.test_get_ip_address_util()
    self.assertEqual(type(ip_addr), type(''))
    self.assertEqual(len(ip_addr.split('.')), 4)

  """
  The values that are asserted:
  -status of the copy web_checkserver process
  """

  def test_copy_web_checkserver_script(self):
    status = dev_util.test_copy_web_checkserver_script_util()
    self.assertEqual(status, 0)

  """
  The values that are asserted:
  -status of the copy do_install process
  """

  def test_do_install(self):
    status = dev_util.test_do_install_util()
    self.assertEqual(status, 0)


# notice: when this script is run directly everything is ok but when it is imported
#  as a module inside another script, the MyTest class is not defined
if __name__ == '__main__':
  dev_util.sync_time()
  unittest.main()
