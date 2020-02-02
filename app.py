import click
from kubernetes import client, config
import requests

def get_image_hash(docker_registry, artifactory_auth, image_name, image_tag):
    response = requests.get(f"https://{docker_registry}/v2/{image_name}/manifests/{image_tag}", headers={
                            "Accept": "application/vnd.docker.distribution.manifest.v2+json"}, auth=artifactory_auth)
    content_digest = response.headers.get("Docker-Content-Digest")
    if "sha256" in content_digest:
        return content_digest[content_digest.index(":")+1:]


def scan_image(image, docker_registry, xray_url,artifactory_auth):
    if docker_registry not in image:
        return None

    image_hash = image[image.index(":")+1:]

    if "@sha256" not in image:
        image_name = image[image.index("/"):image.index(":")]
        image_hash = get_image_hash(docker_registry, artifactory_auth, image_name, image_hash)

    if image_hash == None:
        return None

    request = {"checksums": [image_hash]}
    response = requests.post(f"{xray_url}/api/v1/summary/artifact",
                             json=request, auth=artifactory_auth).json()
    issue_count = 0
    if response["artifacts"] and len(response["artifacts"]) > 0 and len(response["artifacts"][0]["issues"]) > 0:
        for issue in response["artifacts"][0]["issues"]:
            if issue["severity"] == "High":
                issue_count += 1

    return issue_count


@click.command()
@click.option(
    "--namespace",
    help="Analyze pods only in this namespace, check all if omitted.",
    default="defaut",
    envvar="NAMESPACE",
)
@click.option(
    "--docker-registry",
    help=f"Docker Registries to scan (e.g. docker.my-company.com)",
    envvar="DOCKER_REGISTRY",
    prompt=True
)
@click.option(
    "--xray-url",
    help=f"URL for your Xray instance (e.g. https://xray.my-company.com)",
    envvar="DOCKER_REGISTRY",
    prompt=True
)
@click.option(
    "--artifactory-username",
    help=f"User to use for auhtentication against Artifactory/Xray API",
    envvar="ARTIFACTORY_USERNAME",
    prompt=True
)
@click.option(
    "--artifactory-password",
    help=f"Password to use for auhtentication against Artifactory/Xray API",
    envvar="ARTIFACTORY_PASSWORD",
    prompt=True,
    hide_input=True
)
def main(namespace, docker_registry, xray_url, artifactory_username, artifactory_password):

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    print("Listing pods with their images:")

    if namespace:
        ret = client.CoreV1Api().list_namespaced_pod(namespace)
    else:
        ret = client.CoreV1Api().list_pod_for_all_namespaces()

    for i in ret.items:
        for container in i.spec.containers:
            issue_count = scan_image(
                container.image, docker_registry, xray_url, (artifactory_username, artifactory_password))
            print("%s\t%s\t%s\t%s" % (i.metadata.namespace,
                                      i.metadata.name, container.image, issue_count))


if __name__ == "__main__":
    main()
