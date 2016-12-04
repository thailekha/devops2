import util

logger = util.Logger()

"""
Get the CPU usage of the currently connected instance
Argument(s):
-ip address of the instance
Returns
-CPU percentage in float or None
"""


def get_cpu_usage(instance_ip):
  (status, output) = util.ssh_exec(instance_ip,
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