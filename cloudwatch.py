#!/usr/bin/python3

import boto.ec2, boto.ec2.cloudwatch, pprint, datetime, sys
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
  if len(sys.argv) == 3:
    instance_ip = '-'.join(sys.argv[1].split('.'))
    ec2_conn = boto.ec2.connect_to_region('us-west-2',
                                          aws_access_key_id=sys[1],
                                          aws_secret_access_key=sys[2])
    cw = boto.ec2.cloudwatch.connect_to_region('us-west-2',
                                               aws_access_key_id=sys[1],
                                               aws_secret_access_key=sys[2])

    # pp(cw.describe_alarms())
    # list all metrics
    # all_metrics = cw.list_metrics()

    get_stats(cw, ec2_conn, 'CPUUtilization', 'AWS/EC2', 'i-0f18e6168b19416d4')
  else:
    logger.log('Cannot parse credentials', 'e')

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

  # pp(namespaces)

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

  # pp(as_metrics)

# ===========================================================================================
# list metrics of ec2 namespace
# ===========================================================================================
"""
{'CPUCreditBalance': 21,
 'CPUCreditUsage': 19,
 'CPUUtilization': 20,
 'DiskReadBytes': 20,
 'DiskReadOps': 23,
 'DiskWriteBytes': 20,
 'DiskWriteOps': 18,
 'NetworkIn': 17,
 'NetworkOut': 22,
 'NetworkPacketsIn': 16,
 'NetworkPacketsOut': 14,
 'StatusCheckFailed': 18,
 'StatusCheckFailed_Instance': 18,
 'StatusCheckFailed_System': 14}
"""

def list_ec2_metrics(all_metrics):
  ec2_metrics = {}
  for i in all_metrics:
    if i.namespace == 'AWS/EC2':
      if i.name in ec2_metrics:
        ec2_metrics[i.name] += 1
      else:
        ec2_metrics[i.name] = 1

  # pp(ec2_metrics)

# ===========================================================================================
# list all namespaces and dimensions
# ===========================================================================================
"""
{'CPUCreditBalance': [{'InstanceId': ['i-0f18e6168b19416d4']},
                      {'InstanceId': ['i-0150c3ce3a86c5beb']},
                      {'InstanceId': ['i-0d631b18e93a20d7c']}],
 'CPUCreditUsage': [{'InstanceId': ['i-0a1505bcf041b9c5e']},
                    {'InstanceId': ['i-0150c3ce3a86c5beb']}],
 'CPUUtilization': [{'InstanceId': ['i-0f18e6168b19416d4']},
                    {'InstanceId': ['i-0d631b18e93a20d7c']},
                    {'InstanceId': ['i-0150c3ce3a86c5beb']}],
 'DiskReadBytes': [{'InstanceId': ['i-0d631b18e93a20d7c']},
                   {'InstanceId': ['i-0a1505bcf041b9c5e']}],
 'DiskReadOps': [{'InstanceId': ['i-0f18e6168b19416d4']},
                 {'InstanceId': ['i-0a1505bcf041b9c5e']},
                 {'InstanceId': ['i-0150c3ce3a86c5beb']}],
 'DiskWriteBytes': [{'InstanceId': ['i-0f18e6168b19416d4']},
                    {'InstanceId': ['i-0150c3ce3a86c5beb']}],
 'DiskWriteOps': [{'InstanceId': ['i-0f18e6168b19416d4']},
                  {'InstanceId': ['i-0150c3ce3a86c5beb']}],
 'NetworkIn': [{'InstanceId': ['i-0d631b18e93a20d7c']},
               {'InstanceId': ['i-0a1505bcf041b9c5e']}],
 'NetworkOut': [{'InstanceId': ['i-0d631b18e93a20d7c']},
                {'InstanceId': ['i-0a1505bcf041b9c5e']}],
 'NetworkPacketsIn': [{'InstanceId': ['i-0f18e6168b19416d4']},
                      {'InstanceId': ['i-0a1505bcf041b9c5e']},
                      {'InstanceId': ['i-0150c3ce3a86c5beb']}],
 'NetworkPacketsOut': [{'InstanceId': ['i-0f18e6168b19416d4']},
                       {'InstanceId': ['i-0150c3ce3a86c5beb']},
                       {'InstanceId': ['i-0d631b18e93a20d7c']}],
 'StatusCheckFailed': [{'InstanceId': ['i-0f18e6168b19416d4']},
                       {'InstanceId': ['i-0150c3ce3a86c5beb']}],
 'StatusCheckFailed_Instance': [{'InstanceId': ['i-0d631b18e93a20d7c']}],
 'StatusCheckFailed_System': [{'InstanceId': ['i-0a1505bcf041b9c5e']},
                              {'InstanceId': ['i-0d631b18e93a20d7c']}]}
"""

def ec2_instance_metrics_dimensions(ec2_conn,all_metrics):
  reservations = ec2_conn.get_all_reservations()
  ids_running = []
  for r in reservations:
    for i in r.instances:
      # only collect running instances
      if i.state == 'running':
        ids_running.append(i.id)

  ec2_dimensions = {}
  for i in all_metrics:
    if i.namespace == 'AWS/EC2':
      if i.name in ec2_dimensions:
        ec2_dimensions[i.name].append(i.dimensions)
      else:
        ec2_dimensions[i.name] = [i.dimensions]

  filterred_ec2_dimensions = {}
  for metric, dimensions in ec2_dimensions.items():
    filterred_dimensions = []
    for d in dimensions:
      if 'InstanceId' in d:
        running_instances_ids = []
        for id in d['InstanceId']:
          if id in ids_running:
            running_instances_ids.append(id)
        if (len(running_instances_ids) > 0):
          filterred_dimensions.append({
            'InstanceId': running_instances_ids
          })
    filterred_ec2_dimensions[metric] = filterred_dimensions

  """
  print('Running instances:')
  pp(ids_running)
  print('Filterred dimensions:')
  pp(filterred_ec2_dimensions)
  """


# ===========================================================================================
# http://stackoverflow.com/questions/16383809/how-do-i-get-the-most-recent-cloudwatch-metric-data-for-an-instance-using-boto

def get_stats(cw, ec2_conn, metric, namespace, instance_id):
  instance = ec2_conn.get_only_instances(instance_ids=[instance_id])[0]
  if 'Name' in instance.tags:
    logger.log(instance.tags['name'])
  logger.log(instance.ip_address + " (" + instance.id + ")")

  pprint(cw.get_metric_statistics(
    300,
    datetime.datetime.utcnow() - datetime.timedelta(seconds=600),
    datetime.datetime.utcnow(),
    metric,
    namespace,
    'Average',
    dimensions={'InstanceId': [instance_id]}
  ))

if __name__ == '__main__':
  main()
