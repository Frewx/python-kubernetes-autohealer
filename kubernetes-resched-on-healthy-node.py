from kubernetes import client, config, watch
import time

# Load Kubernetes configuration
config.load_kube_config()

# Create Kubernetes API client
v1 = client.CoreV1Api()

# Define the node failure threshold (in seconds)
threshold = 300

# Watch for node events
nodes = v1.list_node().items

for node in nodes:
    node_name = node.metadata.name
    node_status = node.status.conditions[-1]

    node_last_heartbeat = int(time.time()) - int(node.status.conditions[-1].last_heartbeat_time.timestamp())

    print("Last heartbeat for node {0} is {1}".format(node.metadata.name,node_last_heartbeat))

    # Check if the node is unresponsive
    if node_last_heartbeat > threshold:

        print("Node {0} is unresponsive".format(node.metadata.name))
        # Get all pods running on the affected node
        pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node.metadata.name}").items

        for pod in pods:
            print("Pods on the responsive nodes are {0} rescheduling on a healthy node...".format(pod.metadata.name))

        # # Reschedule the pods on healthy nodes
        # for pod in pods:
        #     if pod.status.phase == "Running":
        #         pod_name = pod.metadata.name
        #         pod_namespace = pod.metadata.namespace

        #         # Find a healthy node to reschedule the pod on
        #         for node in v1.list_node().items:
        #             if node.status.conditions[-1].status == "True":
        #                 pod.spec.node_name = node.metadata.name
        #                 v1.patch_namespaced_pod(pod_name, pod_namespace, pod)
        #                 break
    else:
        print("Node {0} is responsive".format(node.metadata.name))