import sys, subprocess, time

# ===========================================================================================
# Logger
# ===========================================================================================

"""
Logger class, can be used to print message in color depending on the type of message
More details about the color codes:
http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
https://godoc.org/github.com/whitedevops/colors
"""


class Logger:
  def __init__(self):
    self.on = True

    # TYPES OF MESSAGES, CORRESPONDING TO COLORS
    self.OKGREEN = '\033[92m'
    self.WARNING = '\033[93m'
    self.FAIL = '\033[91m'
    self.BACK_TO_WHITE = '\033[0m'
    # REPORTING THE SUBPROCESS TASK
    self.STATUS = '\033[94m'
    self.OUTPUT = '\033[95m'

    # This is used as the switch-statement to choose which color to use depending on the message type
    self.switch = {
      'normal': lambda msg: str(msg),
      # error
      'e': lambda msg: self.FAIL + str(msg) + self.BACK_TO_WHITE,
      # warning
      'w': lambda msg: self.WARNING + str(msg) + self.BACK_TO_WHITE,
      # success
      's': lambda msg: self.OKGREEN + str(msg) + self.BACK_TO_WHITE,
      # status
      'st': lambda msg: self.STATUS + str(msg) + self.BACK_TO_WHITE,
      # output
      'o': lambda msg: self.OUTPUT + str(msg) + self.BACK_TO_WHITE,
      'default': lambda msg: self.WARNING + str(msg) + ' *ERROR MESSAGE TYPE, CHECK LOGGER CLASS*' + self.BACK_TO_WHITE,
    }

  """
  Print a message
  """

  def log(self, msg, msgType='normal'):
    if self.on:
      if msgType in self.switch:
        print('Logger:', self.switch.get(msgType)(msg))
      else:
        print('Logger:', self.switch.get('default')())


# ===========================================================================================
# logger instance
# ===========================================================================================

logger = Logger()

# ===========================================================================================
# User interface (menu)
# ===========================================================================================

"""
This method accepts a message to be printed out as a welcome message to the menu. It also accepts a list of menu items
"""


def show(msg, menu_items):
  print(msg, '(input \033[91m-99\033[0m to go back or exit)')
  choice = __menu__(menu_items)
  return choice


"""
Print all the menu items preceded by the index so that user can make choice, if the choice is not valid, the method prompts the user again. -99 is used as the special exit value
"""


def __menu__(options):
  while True:
    for indx, val in enumerate(options):
      print(str(indx) + ')', val)
    try:
      choice = int(input('===>'))
      valid_option = choice < len(options) and choice >= 0
      exit_option = choice == -99  # -99 is exit
      if valid_option or exit_option:
        # if only choice is used instead of str(choice), exception thrown
        logger.log('Chosen option: ' + str(choice), 's')
        return choice
      else:
        logger.log('Invalid choice, please try again', 'w')
    except:
      logger.log('Invalid input, please try again', 'e')
      logger.log(sys.exc_info()[0], 'e')


# ===========================================================================================
# utility methods
# ===========================================================================================

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
