from kubernetes import client, config
import datetime

def delete_pods(node_name,EVICTION_GRACE_PERIOD_SECONDS):
    # Create the Kubernetes API client
    v1 = client.CoreV1Api()

    # Define a label selector to select only pods that don't have the k8s-app label
    label_selector = f"spec.nodeName={node_name},!k8s-app"

    # Get all the pods that match the labels running on the unresponsive node
    pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}",label_selector=label_selector).items
    
    if len(pods) > 0:
        # For each pod, delete the pod with grace period
        for pod in pods:
            print("Deleting pod {0}".format(pod.metadata.name))
            v1.delete_namespaced_pod(
                pod.metadata.name,
                pod.metadata.namespace,
                body=client.V1DeleteOptions(grace_period_seconds=EVICTION_GRACE_PERIOD_SECONDS, propagation_policy='Background')
            )
    else:
        print("There is no pod on unresponsive node")

def check_node_status(node_name):
    # Create the Kubernetes API client
    v1 = client.CoreV1Api()
    # Get the node status
    node = v1.read_node_status(node_name)

    # Check if the node is ready
    for condition in node.status.conditions:
        if condition.type == "Ready" and condition.status != "True":
            return False

    return True

def search_unresponsive_nodes():
    # Eviction grace period in seconds
    EVICTION_GRACE_PERIOD_SECONDS = 0 # NOTE: ugurakgul - we are forcing the delete

    # Create the Kubernetes API client
    v1 = client.CoreV1Api()
    # Get all the nodes
    nodes = v1.list_node().items

    for node in nodes:
        # Check if the node is unresponsive
        if not check_node_status(node.metadata.name):
            print("Node: {0} is not responsive, deleting pods...".format(node.metadata.name))
            # Forcefully delete the pods from the unresponsive node
            delete_pods(node.metadata.name,EVICTION_GRACE_PERIOD_SECONDS) 
            # When we delete the pods, because of the replicas, new pods will be deployed on the responsive nodes
            print("---------------------")

def main(kubeconfig):
    # Load Kubernetes configuration
    config.load_kube_config(config_file=kubeconfig)
    # # Define the check interval seconds
    CHECK_INTERVAL_SECONDS = 10
    print("---------------------")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("---------------------")
    print("Searching unresponsive nodes...")
    # while True:
    search_unresponsive_nodes()
        # time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
