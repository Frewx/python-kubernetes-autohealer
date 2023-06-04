from kubernetes import client, config, utils
import datetime

def pod_health_checker(namespace,label_selector):

    # Create Kubernetes API clients
    v1 = client.CoreV1Api()
    custom_objects_api = client.CustomObjectsApi()

    # Get all pods in the default namespace
    pods = v1.list_namespaced_pod(namespace,label_selector=label_selector).items

    #Get the pods' usage metrics
    pod_metrics = custom_objects_api.list_namespaced_custom_object(group="metrics.k8s.io",version="v1beta1", namespace=namespace, plural="pods")["items"]

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

    #Handle if cpu or memory usage is 0
    if used_cpu_percent == 0 or used_mem_percent == 0:
        if replicas != 1:
            print("Used CPU is 0 but replicas are {0}, scaling down the deployment.".format(replicas))
            print("---------------------")
            replicas = appsv1.read_namespaced_deployment(deployment_name, namespace).spec.replicas
            appsv1.patch_namespaced_deployment_scale(deployment_name, namespace, {"spec": {"replicas": replicas - 1}})

        else:
            print("Used CPU percent is 0 skipping autoscaling...") #TODO: ugurakgul: Can we throw some errors here ?
            print("---------------------")

    elif used_cpu_percent > threshold or used_mem_percent > threshold:
            print("Usage is bigger than the threshold: {0}. Scaling up the deployment...".format(threshold))
            print("---------------------")

            replicas = appsv1.read_namespaced_deployment(deployment_name, namespace).spec.replicas
            appsv1.patch_namespaced_deployment_scale(deployment_name, namespace, {"spec": {"replicas": replicas + 1}})
    else:
        if replicas == 1:
            print("Usage is lower than the threshold: {0} but replica count is only 1, cannot scale down the deployment.".format(threshold))
            print("---------------------")

        else:
            print("Usage is lower than the threshold: {0} and the replica count is bigger than 1, scaling down the deployment...".format(threshold))
            print("---------------------")
            replicas = appsv1.read_namespaced_deployment(deployment_name, namespace).spec.replicas
            appsv1.patch_namespaced_deployment_scale(deployment_name, namespace, {"spec": {"replicas": replicas - 1}})


def main(namespace,deployment,label_selector,threshold,kubeconfig):
    # Load Kubernetes configuration
    config.load_kube_config(config_file=kubeconfig)

    print("---------------------")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("---------------------")
    
    used_cpu_percent,used_mem_percent = pod_health_checker(namespace,label_selector)
    pod_autoscaler(namespace,deployment,threshold,used_cpu_percent,used_mem_percent)


if __name__ == "__main__":
    main()
