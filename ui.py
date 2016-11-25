#!/usr/bin/python3
import logger
import sys

logger = logger.Logger()

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


if __name__ == '__main__':
  print('This is a menu module')
