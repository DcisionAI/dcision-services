# DcisionAI Multi-Cloud Deployments

This folder contains all infrastructure-as-code and deployment resources for running the DcisionAI solver-service and mcp-service locally, on Kubernetes, or in any major cloud (GCP, AWS, Azure).

## Local Development

Use Docker Compose to run both services locally:

```sh
docker-compose up --build
```
- MCP service: http://localhost:3000
- Solver service: http://localhost:8080

## Kubernetes

Apply the manifests in the `k8s/` directory:

```sh
kubectl apply -f k8s/
```

## Helm

Install both services using the Helm chart in `helm/`:

```sh
helm install dcisionai ./helm
```

## Terraform (Cloud)

Deploy to GCP, AWS, or Azure using the Terraform modules in `terraform/`:

```sh
cd terraform
terraform init
terraform apply -var="cloud=gcp" ...
```
- For AWS: `-var="cloud=aws" ...`
- For Azure: `-var="cloud=azure" ...`

See each cloud's subfolder for more details and required variables.

## Environment Variables

- `SOLVER_SERVICE_URL` (for MCP)
- `PORT` (for both services)

## Customer Deployment

- See this folder for Docker Compose, K8s, Helm, and Terraform templates.
- For help, contact support@dcisionai.com or see the [docs](https://yourcompany.com/docs). 