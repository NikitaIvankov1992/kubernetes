import argparse, traceback, re, json, sys
from datetime import datetime, timedelta
from kubernetes import client, config


#wrapper for kubernetes API
class wrapper:
  def __init__(self, config_file, context):
    '''
    Simple logic here:
    In case we launch the script manually - check kubeconfig(file and context may be changed via args),
    otherwise - script gets service token embded as container's volume,
    if neither kubeconfig nor toket gotten - exit program
    '''
    try:
      self.config = config.load_kube_config(config_file, context)
    except config.config_exception.ConfigException:
      print(f'You made a mistake when specifying the arguments, more details listed below\n{traceback.format_exc()}')
      sys.exit()
    except Exception as e:
      try:
        self.config = config.load_incluster_config()
      except Exception as e:
        print(f'Neither kubeconfig nor token has been gotten, more details listed below\n{traceback.format_exc()}')
        sys.exit()

    # object for v1 API calls
    self.CoreV1Api = client.CoreV1Api()

  def get_all_pods(self):
    '''
    Here we get list of the pods,
    return - list of V1Container objects
    '''
    try:
      return self.CoreV1Api.list_pod_for_all_namespaces(timeout_seconds=60).items
    except Exception as e:
      print(f'Exception raised while getting pods, most probably you dont have appropriate rights, more details listed below\n{traceback.format_exc()}')
      sys.exit()

  def check_pods(self):
    '''
    Check of the following rules:
    1)image_prefix - whether the image of container(or containers) inside the pod prefixed with "bitnami/" or not, result - boolean
    2)team_label_present - whether the pod contains a label `team` with some value, result - boolean
    3)recent_start_time - whether the pod has been launched more than 7 days ago(according to it's `startTime`), result - boolean

    The output is STDOUT in json format
    '''
    for pod in self.get_all_pods():
      '''
      "result" dict is created per pod, 
      it consists of name of the pod and list of rules evaluation
      '''
      result = {'pod': '', 'rule_evaluation': []}
      result['pod'] = pod.metadata.name

      '''
      original datetime - an object without timezone,
      kubernetes gives us the date of pod creation which includes timezone,
      hence we add gotten timezone to the original datetime object and compare both objects  
      '''
      recent_start = pod.metadata.creation_timestamp >= datetime.now().replace(tzinfo=pod.metadata.creation_timestamp.tzinfo) - timedelta(7)

      # simple check if "labels" object exists
      if pod.metadata.labels is not None:
          team_label = 'team' in pod.metadata.labels
      else:
          team_label = False

      for container in pod.spec.containers:
          # local result for each container inside the pod
          local_result = [{"name": "recent_start_time", "valid": recent_start}, {"name": "team_label_present", "valid": team_label}]

          local_result.insert(0, {"name": "image_prefix", "valid": True if(re.match(r'^bitnami/.*', container.image)) else False})

          '''
          if the pod consists of the only container and this is the first cycle
          rule_evaluation is equal to local_result
          otherwise(more than one container in the pod)
          append new evaluation result to list
          '''
          if not result['rule_evaluation'] and len(pod.spec.containers) == 1:
            result['rule_evaluation'] = local_result
          else:
            result['rule_evaluation'].append(local_result)

      print(json.dumps(result))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--config_file', default=None,
                        help='Kubeconfig file location')
  parser.add_argument('--context', default=None,
                        help='What context to use')
  args = parser.parse_args()

  wrapper(args.config_file, args.context).check_pods()
