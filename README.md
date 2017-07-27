# Openshift Pod Watcher

This repository implements a python based opensfhit pod which will monitor pods within namespaces and create events based on pod status and the number of restarts within a given threashold.   There is a status page at the root of the project displaying the current information and a rest endpoint which can be called to get current pod alerts.  Once the alerts are retrieved they are reset to normal state.

## Pod Watch Setup

To use this with OpenShift, it is a simple matter of creating a new application within OpenShift, pointing the S2I builder at the Git repository containing your static web site.


```
Name:		httpd-server
Description:	Apache HTTPD Server
Annotations:	tags=instant-app,httpd

Parameters:
    Name:		APPLICATION_NAME
    Description:	The name of the application.
    Required:		true
    Value:		httpd-server

    Name:		SOURCE_REPOSITORY
    Description:	Git repository for source.
    Required:		true
    Value:		<none>
    
    Name:		SOURCE_DIRECTORY
    Description:	Sub-directory of repository for source files.
    Required:		false
    Value:		<none>

As an example, to build and host a simple site with you only need run:

```
oc new-app getwarped/s2i-httpd-server~https://github.com/getwarped/httpd-site-maintenance --name site-maintenance

oc expose svc/site-maintenance
```

```
