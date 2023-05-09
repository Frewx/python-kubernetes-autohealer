import autoscale,unresponsive_nodes,time

def main():
  KUBECONFIG=""
  namespace = "default"
  deployment = "nginx-deployment"
  label_selector = "app=nginx"
  threshold = 0.8
  CHECK_INTERVAL_SECONDS = 10
  while True:
    autoscale.main(namespace,deployment,label_selector,threshold,KUBECONFIG)
    unresponsive_nodes.main(KUBECONFIG)
    time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()