# Openshift Pod Watcher

This repository implements a python based opensfhit pod which will monitor pods within namespaces and create events based on pod status and the number of restarts within a given threashold.   There is a status page at the root of the project displaying the current information and a rest endpoint which can be called to get current pod alerts.  Once the alerts are retrieved they are reset to normal state.

## Pod Watch Setup

To use this with OpenShift, it is a simple matter of creating a new application within OpenShift, pointing the Python S2I builder at the Git repository containing this code.

```
Name:		pod-watcher
Description:	Python service to monitor pod restarts and crashes

Parameters:
    Name:		OPENSHIFT_HOST
    Description:	The host of the openshift API service.
    Required:		true
    Default:        <none>

    Name:		OPENSHIFT_NAMESPACE
    Description:	A list of namespaces to monitor pod restarts
    Required:		true
    Default:		<none>
    
    Name:		OPENSHIFT_TOKEN
    Description:	The openshift authentication token of the service account used to run the pod.  The service 
                     must have the view role on the namespaces it is watching.
    Required:		true
    Default:		<none>

    Name:		PODMONITOR_FILEPATH
    Description:	The file path the pod uses to persist the current status.
    Required:		true
    Default:		/var/tmp/

As an example, to create a new pod monitor instance using the python s2i build image:

```
oc create sa podmonitorsa    

-- Get token of the service account for configuring service or "use oc whoami -t" for a temporary token


oc new-app openshift/python:3.4~https://github.com/malacourse/pod-watcher.git -e OPENSHIFT_HOST=192.168.99.100:8443 -e OPENSHIFT_NAMEPACE=test,jenkins -e OPENSHIFT_TOKEN=4AOesX1gKRZ4RQEty18KxuzvzN9OSDg3VtKRtmvCRgk --name pod-monitor
                     
                     
oc expose svc/pod-monitor
oc policy add-role-to-user view system:serviceaccount:test:podwatchersa -n test
oc policy add-role-to-user view system:serviceaccount:test:podwatchersa -n jenkins

```
```
## Pod Watch Usage

To use this with OpenShift, it is a simple matter of creating a new application within OpenShift, pointing the Python S2I builder at the Git repository containing this code.
