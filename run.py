#!/usr/bin/python3
import sys, logging
import util, monitor, cloudwatch

logger = util.Logger()


def menu():
  try:
    flag = True
    while (flag):
      option = util.show('Please choose a task ',
                         ['Check CPU', 'Cloudwatch metrics'])
      if option == 0:
        # Check CPU
        monitor.get_cpu_usage('-'.join(input('IP address: ').split('.')))
      elif option == 1:
        cloudwatch.main()
      elif option == -99:
        flag = False
  except:
    logger.log(sys.exc_info()[0], 'e')
    logging.exception('EXCEPTION')


if __name__ == '__main__':
  menu()
