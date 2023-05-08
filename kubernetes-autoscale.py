from kubernetes import client, config, utils

def pod_health_checker():
    # Load Kubernetes configuration
    config.load_kube_config()

    # Create Kubernetes API clients
    v1 = client.CoreV1Api()
    custom_objects_api = client.CustomObjectsApi()

    # Get all pods in the default namespace
    pods = v1.list_namespaced_pod(namespace="default").items

    #Get the pods' usage metrics
    pod_metrics = custom_objects_api.list_namespaced_custom_object(group="metrics.k8s.io",version="v1beta1", namespace="default", plural="pods")["items"]

    #Parse string values into integer
    for pod in pod_metrics:

        parsed_cpu_usage = utils.parse_quantity(pod["containers"][0]["usage"]["cpu"])
        parsed_mem_usage = utils.parse_quantity(pod["containers"][0]["usage"]["memory"])

    #Begin calculations
    for pod in pods:
        
        limits = pod.spec.containers[0].resources.limits
        
        parsed_cpu_limits = utils.parse_quantity(limits["cpu"])
        parsed_mem_limits = utils.parse_quantity(limits["memory"])


        print("Parsed CPU usage:{0} and CPU limit:{1}".format(parsed_cpu_usage,parsed_cpu_limits))
        print("Parsed memory usage:{0} and memory limit:{1}".format(parsed_mem_usage,parsed_mem_limits))

        used_cpu_percent = parsed_cpu_usage / parsed_cpu_limits
        used_mem_percent = parsed_mem_usage / parsed_mem_limits

        print("Used cpu percent is",used_cpu_percent)
        print("Used memory percent is",used_mem_percent)

        return used_cpu_percent,used_mem_percent
    
def pod_autoscaler(namespace,deployment_name,threshold,used_cpu_percent,used_mem_percent):

    # v1 = client.CoreV1Api()
    appsv1 = client.AppsV1Api()
    # Define the resource limit and request threshold for scaling
    replicas = appsv1.read_namespaced_deployment(deployment_name, namespace).spec.replicas

    #Handle if cpu and memory usage is 0
    if used_cpu_percent == 0 or used_mem_percent == 0:
        print("Used CPU percent is 0 skipping autoscaling...") #TODO: ugurakgul: Can we throw some errors here ?

    elif used_cpu_percent > threshold or used_mem_percent > threshold:
            print("Usage is bigger than the threshold: {0}. Scaling up the deployment...".format(threshold))
            
            replicas = appsv1.read_namespaced_deployment(deployment_name, namespace).spec.replicas
            appsv1.patch_namespaced_deployment_scale(deployment_name, namespace, {"spec": {"replicas": replicas + 1}})
    else:
        if replicas == 1:
            print("Usage is lower than the threshold: {0} but replica count is only 1, cannot scale down the deployment.".format(threshold))

        else:
            print("Usage is lower than the threshold: {0} and the replica count is bigger than 1, scaling down the deployment...".format(threshold))
            replicas = appsv1.read_namespaced_deployment(deployment_name, namespace).spec.replicas
            appsv1.patch_namespaced_deployment_scale(deployment_name, namespace, {"spec": {"replicas": replicas - 1}})


def main():
    used_cpu_percent,used_mem_percent = pod_health_checker()
    pod_autoscaler("default","nginx-deployment",0.5,used_cpu_percent,used_mem_percent)

if __name__ == "__main__":
    main()

    # replicas = appsv1.read_namespaced_deployment(deployment_name, "default").spec.replicas
    # print("replicas for pod {0} is {1}".format(pod.metadata.name,replicas))

#     # Check if the pod is using more than the threshold of its resources
#     if used_cpu_percent > threshold or used_mem_percent > threshold:
#         # Scale up the deployment
#         deployment_name = pod.metadata.labels["app"]
#         replicas = v1.read_namespaced_deployment(deployment_name, "default").spec.replicas
#         v1.patch_namespaced_deployment_scale(deployment_name, "default", {"spec": {"replicas": replicas + 1}})
#     else:
#         # Scale down the deployment
#         deployment_name = pod.metadata.labels["app"]
#         replicas = v1.read_namespaced_deployment(deployment_name, "default").spec.replicas
#         v1.patch_namespaced_deployment_scale(deployment_name, "default", {"spec": {"replicas": replicas - 1}})