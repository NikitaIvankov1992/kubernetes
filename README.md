# Pods checker

**General overview**

The script has been created for simple evaluation of following rules
- ensure the pod only uses images prefixed with 'bitnami/'
- ensure the pod contains a label 'team' with some value
- ensure the pod has not been running for more than 7 days according to it's 'startTime'

The evaluation result should be outputted on stdout in JSON log format one line per pod

**How to use**

There are three possible way how to launch the script
- Manually
- Job managed by Cronjob controller
- Pod within the cluster

1. **Manual execution**

The simplest way to get the result is to launch python script, you must do it in the following order:

- Clone the git repository on your workstation <br />
``` git clone https://github.com/NikitaIvankov1992/kubernetes.git```

- Create virtualenv with <br />
```python3 -m venv checker_env```

- Activate the virtualenv <br />
```source checker_env/bin/activate```

- Go to git folder <br />
```cd kubernetes```

- Install dependencies <br />
```pip3 install -r requirements.txt```

- Launch the script <br />
```python3 checker.py```

During execution the script looks for a kubeconfig file(by default stored at ~./kube/)
You can overwrite this behavior by specifying the location of kubeconfig file via --config_file argument(you can also use --context argument to rewrite context value as well)

Here the launching command may look like the following <br />
```python checker.py --config_file path/to/the/kubeconfig --context name_of_the_context```

2. **Job** <br />

If you want to launch the script on a daily basis, you can create a cronjob which will do this work for you, just follow the steps below:

- As the application packed into a simple Docker container, you should store it somewhere(public github repo or your own private repository). 
Now it's stored at the github as following 'ivankovnikita/checker'.
You can create your own image, following the steps:

	- Clone the git repository on your workstation <br />
	``` git clone https://github.com/NikitaIvankov1992/kubernetes.git```
	
	- Go to the folder <br />
	```cd kubernetes```

	- Build new image <br />
	``` docker image build -t {you_repository}/{image_name} .```
 
	- Push created image to repository <br />
	``` docker push {you_repository}/{image_name} ```

- When the image is ready, pull the repository from github to your workstation
``` git clone https://github.com/NikitaIvankov1992/kubernetes.git``` (in case the station you build image on and the station you use for deploying k8s objects aren't the same, otherwise you can skip this step) <br />

- Go to git folder <br /> 
```cd kubernetes```

- In the 'job' folder you could find objects for the deployment, 'job.yaml' consists the schedule for launching and the image to launch, you can mutate it for your needs

- When all preparations are done, deploy the application <br />
``` kubectl apply -f git/root/folder/job```

- To get the result of the job execution execute following command when the recent job is completed <br />
``` kubectl logs {name_of_the_pod_launched_by_job}```


3. **Pod** <br />

If you don't want to wait until the job is executed or don't want to use jobs for any other reason, you could launch the application as s simple pod, in this case you must follow the same steps as in the previous example, but deploy manifests from another folder<br />

``` kubectl apply -f git/root/folder/pod```

For getting the result use <br />

``` kubectl logs pods-checker ```
command <br />

In second and third cases instead of kubeconfig service account will be used.

**All the above tested on v1.20.0 cluster version**




