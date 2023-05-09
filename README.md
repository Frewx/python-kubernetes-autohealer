# python-kubernetes-autohealer
This repository contains some python codes for kubernetes autohealing processes.

* kubernetes-resched-on-healthy-node.py will delete stuck pods on unresponsive nodes, if using replicasets, the pods will be scheduled on the healthy nodes.
