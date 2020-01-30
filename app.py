from kubernetes import client, config

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1 = client.CoreV1Api()
print("Listing pods with their images:")
# ret = v1.list_namespaced_pod(namespace="derkoe", watch=False)
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    for container in i.spec.containers:
        print("%s\t%s\t%s" % (i.metadata.namespace, i.metadata.name, container.image))
