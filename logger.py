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

  """
  Stop the logger from printing
  """

  def switch_off(self):
    self.on = False

  """
  Let the logger print again
  """

  def switch_on(self):
    self.on = True


if __name__ == '__main__':
  print('This is a logging utility')
