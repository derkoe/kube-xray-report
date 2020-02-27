# Kubernetes Xray Report

Generates a report showing the security issue count of all images currently
running on your cluster.

## Usage

Create a secret with your Artifactory/Xray URLs and authentication:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name:  kube-xray-report-env
type: Opaque
stringData:
   DOCKER_REGISTRY: your-artifactory-registry.example.com
   ARTIFACTORY_USERNAME: artifactory_user
   ARTIFACTORY_PASSWORD: artifactory_password
   XRAY_URL: https://your-xray-server.example.com
```

Then create the resources defined in `deploy` folder with:

    kubectl apply -f deploy/

You can take a look at the report by running

    kubectl port-forward service/kube-xray-report 8080:80

and then opening your browser at http://localhost:8080/.
