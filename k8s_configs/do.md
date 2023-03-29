

`doctl kubernetes cluster kubeconfig save a91c8a64-a8c4-459d-a98d-1cff8e88c25d`

REDIS
`rediss://default:AVNS_9ZcQQxUCrLaSY41kwB1@db-redis-nyc3-67768-do-user-10228058-0.b.db.ondigitalocean.com:25061`
`rediss://default:AVNS_9ZcQQxUCrLaSY41kwB1@private-db-redis-nyc3-67768-do-user-10228058-0.b.db.ondigitalocean.com:25061`

Command
Description
kubectl config get-contexts
Lists your cluster name, user, and namespace
kubectl cluster-info
Display addresses of the control plane and cluster services
kubectl version
Display the client and server k8s version
kubectl get nodes
List all nodes created in the cluster
kubectl help
Displays commands that help manage your cluster


Command
Description
doctl kubernetes cluster kubeconfig show <cluster-id|cluster-name>
Show your cluster's kubeconfig YAML
doctl kubernetes
Displays a variety of commands that help manage your cluster via Digitalocean's API
