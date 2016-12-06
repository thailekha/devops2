#!/usr/bin/python3

import boto, boto.ec2, boto.ec2.cloudwatch, pprint, datetime, sys, getpass
import util

logger = util.Logger()


def pp(text):
  pprint.pprint(text)


"""
Attributes of a metric:

['Statistics',
 'Units',
 'connection',
 'create_alarm',
 'describe_alarms',
 'dimensions',
 'endElement',
 'member',
 'name',
 'namespace',
 'query',
 'startElement']

(used dir)
"""


def main():
  register_credentials = True
  while (register_credentials):
    logger.log('Please provide credentials, or input -99 to exit', 'w')
    key_id = getpass.getpass('Key ID: ')
    if key_id == '-99':
      return
    logger.log('key length: ' + str(len(key_id)),'st')
    secret = getpass.getpass('Secret: ')
    if secret == '-99':
      return
    logger.log('key length: ' + str(len(secret)),'st')

    ec2_conn = boto.ec2.connect_to_region('us-west-2',
                                          aws_access_key_id=key_id,
                                          aws_secret_access_key=secret)
    cw = boto.ec2.cloudwatch.connect_to_region('us-west-2',
                                               aws_access_key_id=key_id,
                                               aws_secret_access_key=secret)
    logger.log('Credentials added', 's')
    logger.log('Retrieving metrics ...', 'w')
    running_instances_metrics = None
    try:
      running_instances_metrics = get_running_instances_metrics(ec2_conn, cw.list_metrics(
        # all dimensions with InstanceId name
        dimensions={
          'InstanceId': None
        },
        namespace='AWS/EC2'
      ))
      register_credentials = False
    except:
      logger.log(sys.exc_info()[0], 'e')
      logger.log('Error adding credentials, please try again', 'e')

  metrics_list = sorted(list(running_instances_metrics.keys()))
  logger.log('Done', 'w')

  flag = True
  while (flag):
    option = util.show('Choose metric:', metrics_list)
    if option >= 0 and option < len(metrics_list):
      print_stats(cw, ec2_conn, metrics_list[option], 'AWS/EC2', running_instances_metrics[metrics_list[option]])
    elif option == -99:
      flag = False


# ===========================================================================================
# dictionary of metrics mapped to instance ids
# ===========================================================================================

def get_running_instances_metrics(ec2_conn, ec2_metrics):
  reservations = ec2_conn.get_all_reservations()
  ids_running = []
  for r in reservations:
    for i in r.instances:
      # only collect running instances
      if i.state == 'running':
        ids_running.append(i.id)

  filterred_metrics = {}
  """
  {
    metric_name: [instance_ids]
  }
  """
  for m in ec2_metrics:
    # m.dimensions ==> {'InstanceId': ['i-08b57a1fe9cdb9f61']}
    running_instances_ids = []
    for id in m.dimensions['InstanceId']:
      # check against the list of running instances ids
      if id in ids_running:
        running_instances_ids.append(id)
    if (len(running_instances_ids) > 0):
      if m.name in filterred_metrics:
        filterred_metrics[m.name] += running_instances_ids
      else:
        filterred_metrics[m.name] = running_instances_ids
  return filterred_metrics


# ===========================================================================================
# http://stackoverflow.com/questions/16383809/how-do-i-get-the-most-recent-cloudwatch-metric-data-for-an-instance-using-boto
# print statistics
# ===========================================================================================

def print_stats(cw, ec2_conn, metric, namespace, instance_ids):
  logger.log('Average ' + metric + ' in roughly the last 5 minutes: ', 'o')
  # eg. [{'InstanceId': ['i-0f18e6168b19416d4']}, {'InstanceId': ['i-0150c3ce3a86c5beb']}, {'InstanceId': ['i-0d631b18e93a20d7c']}]
  for instance_id in instance_ids:
    instance = ec2_conn.get_only_instances(instance_ids=[instance_id])[0]
    info = ''
    if 'Name' in instance.tags:
      info += instance.tags['Name'] + " / "
    info += instance.ip_address + " / " + instance_id + ': '

    """
    [{'Average': 0.034,
    'Timestamp': datetime.datetime(2016, 12, 4, 18, 24),
    'Unit': 'Percent'}]
    """

    # "now": the time when this function is called
    result = cw.get_metric_statistics(
      300,  # 300 seconds / 5 minutes period
      datetime.datetime.utcnow() - datetime.timedelta(seconds=400),  # start from 400 seconds ago
      datetime.datetime.utcnow(),  # until now
      metric,
      namespace,
      'Average',
      dimensions={'InstanceId': [instance_id]}
    )[0]

    info += str(result['Average']) + " " + str(result['Unit'])
    logger.log(info, 'st')


# ===========================================================================================
# some other functions thtat maybe helpful
# ===========================================================================================

# ===========================================================================================
# list all namespaces
# ===========================================================================================
"""
{'AWS/AutoScaling': 8,
 'AWS/EBS': 151,
 'AWS/EC2': 260,
 'AWS/ELB': 67,
 'AWS/S3': 2,
 'AWS/SNS': 2}
"""


def print_namespaces(all_metrics):
  namespaces = {}
  for i in all_metrics:
    if i.namespace in namespaces:
      namespaces[i.namespace] += 1
    else:
      namespaces[i.namespace] = 1
  pp(namespaces)


# ===========================================================================================
# list metrics of autoscaling namespace
# ===========================================================================================
"""
{'GroupDesiredCapacity': 1,
 'GroupInServiceInstances': 2,
 'GroupPendingInstances': 2,
 'GroupTerminatingInstances': 1,
 'GroupTotalInstances': 2}
"""


def print_atuoscaling_metrics(all_metrics):
  as_metrics = {}
  for i in all_metrics:
    if i.namespace == 'AWS/AutoScaling':
      if i.name in as_metrics:
        as_metrics[i.name] += 1
      else:
        as_metrics[i.name] = 1
  pp(as_metrics)


# ===========================================================================================
# list metrics of ec2 namespace
# ===========================================================================================

def list_ec2_metrics(all_metrics):
  ec2_metrics = {}
  for i in all_metrics:
    if i.namespace == 'AWS/EC2':
      if i.name in ec2_metrics:
        ec2_metrics[i.name] += 1
      else:
        ec2_metrics[i.name] = 1
  pp(ec2_metrics)


if __name__ == '__main__':
  main()
