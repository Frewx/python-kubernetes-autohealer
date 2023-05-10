# python-kubernetes-autohealer
This repository contains some python codes for kubernetes autohealing processes.

# kubernetes-healthchecker
This program uses two modules to check and heal some of the kubernetes problems such as:
* Having too many load relative to the resources on a pod, will try to scale up the deployment
* Having too few load relative to the resources on a pod, will try to scale down the deployment
* Having unresponsive nodes, will try to forcefully delete the pods on the responsive nodes.

## Modules
### autoscale.py 
Will try to scale up or scale down the given labeled deployment to keep the CPU or Memory usage below the given threshold. 
Uses metrics-server for gathering CPU or Memory metrics.


### unresponsive_nodes.py 
Will delete stuck pods on unresponsive nodes. Doesn't try to move the pods to a responsive node because you can not move a pod from an unresponsive node. If using replicasets, the pods will be scheduled on the healthy nodes if not, the pods simply will be deleted.
