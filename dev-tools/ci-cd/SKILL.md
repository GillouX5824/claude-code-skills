---
name: ci-cd
description: Golden path for CI/CD pipelines at Alter Domus. Use this skill when setting up or modifying GitHub Actions workflows, understanding the branch strategy, or configuring deployment pipelines for Kubernetes. Covers validation (CI) and deploy (CD) pipelines, AWS ECR/EKS integration, Kong deployment, and Checkov security scanning.
---

# CI/CD at Alter Domus

This skill provides the golden path for CI/CD pipelines using GitHub Actions at Alter Domus.

**These are templates.** Replace `{{ PLACEHOLDER }}` values with your service-specific configuration. Additional jobs, steps, or environments can be added as needed.

## Pre-requisite: Check if this is an API project

Before configuring pipelines, check if the project is an API (look for `openapi.yaml`, `kong/` directory, or FastAPI/Express source code). If it is, **load the API skill first** (`skill://apis`) to understand the project type (GSP vs Flex) and its conventions — this affects pipeline configuration (e.g. test commands, Kong settings, validation steps).

## Pipeline Overview

All deployable workloads use two GitHub Actions workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **Validation Pipeline** | Pull requests to `main`/`develop` | CI - validate environment, Helm charts, Kong config, Docker build |
| **Deploy Pipeline** | Push to `develop`, `release/*`, `hotfix/*` | CD - deploy to Kubernetes via Helm, deploy Kong config |

## Branch Strategy

```
feature/* or bugfix/*
        │
        ▼ (PR)
    develop ────────────► dev environment
        │
        ▼ (PR)
    release/* ──────────► prd environment
        │
        ▼ (merge)
      main
```

- **`develop`** branch deploys to **dev** environment
- **`release/*`** and **`hotfix/*`** branches deploy to **prd** environment
- PRs trigger validation only (no deployment)

## Directory Structure

```
.github/
├── CODEOWNERS                    # Team ownership for PR reviews
└── workflows/
    ├── validation-pipeline.yaml  # CI - runs on PRs
    └── deploy-pipeline.yaml      # CD - runs on push
```

---

## Validation Pipeline (CI)

The validation pipeline runs on pull requests and validates:

1. **Environment validation** - Checks environment is correctly configured
2. **Helm & Kubernetes validation** - Validates Helm charts, Docker build, and runs security checks (Checkov, Dockle, SBOM)
3. **Kong configuration** - Validates Kong config against OpenAPI spec (dry run)
4. **Publish results** - Posts validation results to the PR

### Template

```yaml
name: Validation

on:
  pull_request:
    branches:
      - main
      - develop
  workflow_dispatch:

env:
  app_name: {{ APP_NAME }}
  container_image_name: {{ CONTAINER_IMAGE_NAME }}
  chart_name: {{ CHART_NAME }}
  dockerfile_location: .

  tag: ${{ github.run_id }}
  charts_folder: ${{ github.workspace }}/helm
  aws_account_id: {{ AWS_ECR_ACCOUNT_ID }}
  aws_region: eu-central-1
  aws_deploy_role: arn:aws:iam::{{ AWS_ECR_ACCOUNT_ID }}:role/Terraform
  aws_secrets_role: arn:aws:iam::{{ AWS_SECRETS_ACCOUNT_ID }}:role/Terraform-Deploy
  source_branch_name: ${{ github.head_ref }}
  checkov_checks_to_skip: CKV_K8S_28,CKV_K8S_37,CKV_K8S_21,CKV_K8S_14,CKV_K8S_43,CKV_K8S_8,CKV_K8S_31,CKV_K8S_40,CKV_K8S_38,CKV_K8S_9,CKV_K8S_20,CKV_K8S_23,CKV_K8S_22,CKV_K8S_35,CKV_K8S_153
  dockle_ignore: CIS-DI-0010,DKL-DI-0004
  environment: ${{ github.base_ref == '' && inputs.environment || github.base_ref }}

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  validate:
    runs-on: ad-global-runners-arm64
    environment: dev
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Validate Environment
      uses: alterdomus/actions/validate-environment@v1

    - name: Run Helm Validation
      uses: AlterDomus/actions/validate-helm-eks@v1
      with:
        image: ${{ env.container_image_name }}
        tag: ${{ env.tag }}
        helm_folder: ${{ github.workspace }}/helm/${{ env.chart_name }}
        values_file: ${{ github.workspace }}/helm/${{ env.chart_name }}/values-${{ env.environment }}.yaml
        app_name: ${{ env.app_name }}
        dockerfile_location: ${{ env.dockerfile_location }}
        environment: ${{ env.environment }}
        aws_account_id: ${{ env.aws_account_id }}
        aws_region: ${{ env.aws_region }}
        aws_deploy_role: ${{ env.aws_deploy_role }}
        sbom_token: ${{ secrets.SBOMTOKEN }}
        dockle_ignore: ${{ env.dockle_ignore }}
        checkov_checks_to_skip: ${{ env.checkov_checks_to_skip }}

    - name: Validate Kong Configuration
      uses: alterdomus/actions/deploy-kong@v2
      with:
        control_plane: cp-dev-pub-01
        api_name: {{ CONTAINER_IMAGE_NAME }}
        openapi_path: openapi.yaml
        kong_folder: kong
        environment: dev
        dry_run: "true"

    - name: Publish PR Results
      uses: alterdomus/actions/publish-validation-results@v1
```

---

## Deploy Pipeline (CD)

The deploy pipeline deploys to the target environment:

1. **Deploy to Kubernetes** - Build Docker image, push to ECR, deploy via Helm (all handled by `deploy-helm-eks`)
2. **Deploy Kong** - Deploy API gateway configuration

### Template

```yaml
name: AWS CD

on:
  push:
    branches:
      - develop
      - release/*
      - hotfix/*
  workflow_dispatch:

env:
  namespace_prefix: {{ NAMESPACE_PREFIX }}
  app_name: {{ APP_NAME }}
  container_image_name: {{ CONTAINER_IMAGE_NAME }}
  chart_name: {{ CHART_NAME }}
  dockerfile_location: .

  tag: ${{ github.run_id }}
  aws_region: eu-central-1
  aws_account_id: {{ AWS_ECR_ACCOUNT_ID }}
  charts_folder: ${{ github.workspace }}/helm/
  aws_deploy_role: arn:aws:iam::{{ AWS_ECR_ACCOUNT_ID }}:role/Terraform
  aws_secrets_role: arn:aws:iam::{{ AWS_SECRETS_ACCOUNT_ID }}:role/Terraform-Deploy
  eks_cluster_nonprd: eks-ceu-nonprd-shared-01
  eks_cluster_nonprd_role: arn:aws:iam::{{ AWS_NONPRD_ACCOUNT_ID }}:role/Terraform-Deploy
  eks_cluster_prd: eks-ceu-prd-shared-01
  eks_cluster_prd_role: arn:aws:iam::{{ AWS_PRD_ACCOUNT_ID }}:role/Terraform-Deploy

permissions:
  id-token: write
  contents: read

jobs:
  deploy-dev:
    if: ${{ github.ref_name == 'develop' }}
    runs-on: ad-global-runners-arm64
    environment: dev
    env:
      environment: dev
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to ${{ env.environment }}
        uses: AlterDomus/actions/deploy-helm-eks@v1
        with:
          image: ${{ env.container_image_name }}
          tag: ${{ env.tag }}
          helm_folder: ${{ github.workspace }}/helm
          values_file: ${{ github.workspace }}/helm/${{ env.chart_name }}/values-${{ env.environment }}.yaml
          app_name: ${{ env.app_name }}
          dockerfile_location: ${{ env.dockerfile_location }}
          environment: ${{ env.environment }}
          aws_region: ${{ env.aws_region }}
          aws_account_id: ${{ env.aws_account_id }}
          aws_deploy_role: ${{ env.aws_deploy_role }}
          eks_cluster_role: ${{ env.eks_cluster_nonprd_role }}
          eks_cluster_name: ${{ env.eks_cluster_nonprd }}
          namespace: ${{ env.app_name }}-${{ env.environment }}
          chart_name: ${{ env.chart_name }}

      - name: Deploy Kong
        uses: alterdomus/actions/deploy-kong@v2
        with:
          control_plane: cp-${{ env.environment }}-pub-01
          api_name: ${{ env.container_image_name }}
          openapi_path: openapi.yaml
          kong_folder: kong
          environment: ${{ env.environment }}

  deploy-prd:
    if: ${{ (startsWith(github.ref_name, 'release/') || startsWith(github.ref_name, 'hotfix/')) }}
    runs-on: ad-global-runners-arm64
    environment: prd
    env:
      environment: prd
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to ${{ env.environment }}
        uses: AlterDomus/actions/deploy-helm-eks@v1
        with:
          image: ${{ env.container_image_name }}
          tag: ${{ env.tag }}
          helm_folder: ${{ github.workspace }}/helm
          values_file: ${{ github.workspace }}/helm/${{ env.chart_name }}/values-${{ env.environment }}.yaml
          app_name: ${{ env.app_name }}
          dockerfile_location: ${{ env.dockerfile_location }}
          environment: ${{ env.environment }}
          aws_region: ${{ env.aws_region }}
          aws_account_id: ${{ env.aws_account_id }}
          aws_deploy_role: ${{ env.aws_deploy_role }}
          eks_cluster_role: ${{ env.eks_cluster_prd_role }}
          eks_cluster_name: ${{ env.eks_cluster_prd }}
          namespace: ${{ env.app_name }}-${{ env.environment }}
          chart_name: ${{ env.chart_name }}

      - name: Deploy Kong
        uses: alterdomus/actions/deploy-kong@v2
        with:
          control_plane: cp-${{ env.environment }}-pub-01
          api_name: ${{ env.container_image_name }}
          openapi_path: openapi.yaml
          kong_folder: kong
          environment: ${{ env.environment }}
```

---

## Variables to Configure

When creating workflows, replace these placeholders with your service-specific values:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{ APP_NAME }}` | Application/namespace group name | `foundation-services` |
| `{{ CONTAINER_IMAGE_NAME }}` | Docker image name | `notifications-api` |
| `{{ CHART_NAME }}` | Helm chart name | `notifications-api` |
| `{{ NAMESPACE_PREFIX }}` | Kubernetes namespace prefix (usually same as APP_NAME) | `foundation-services` |
| `{{ AWS_ECR_ACCOUNT_ID }}` | AWS account ID for ECR | `211125459373` |
| `{{ AWS_SECRETS_ACCOUNT_ID }}` | AWS account ID for Secrets Manager | `145023093167` |
| `{{ AWS_NONPRD_ACCOUNT_ID }}` | AWS account ID for non-prod EKS | `851725580540` |
| `{{ AWS_PRD_ACCOUNT_ID }}` | AWS account ID for prod EKS | `881490100256` |

## GitHub Secrets Required

Configure these secrets in your repository settings:

| Secret | Environment | Description |
|--------|-------------|-------------|
| `SBOMTOKEN` | all | Token for SBOM validation |

## GitHub Environments

Create these environments in your repository settings:

- **dev** - Development environment, auto-deploys from `develop`
- **prd** - Production environment, deploys from `release/*` and `hotfix/*`

## CODEOWNERS

Create `.github/CODEOWNERS` to define team ownership for PR reviews:

```
@AlterDomus/your-team-name
```

This ensures PRs require approval from the specified team.

---

## Custom Actions Reference

The pipelines use custom Alter Domus actions:

| Action | Purpose |
|--------|---------|
| `alterdomus/actions/validate-environment@v1` | Validates environment configuration |
| `AlterDomus/actions/validate-helm-eks@v1` | Validates Helm charts, builds Docker image, runs Checkov/Dockle/SBOM checks |
| `alterdomus/actions/deploy-kong@v2` | Validates (dry run) or deploys Kong configuration |
| `alterdomus/actions/publish-validation-results@v1` | Posts validation results to PR |
| `AlterDomus/actions/deploy-helm-eks@v1` | Builds image, pushes to ECR, deploys to EKS via Helm |

---

## AWS Infrastructure

### EKS Clusters

| Environment | Cluster | Region |
|-------------|---------|--------|
| Non-production | `eks-ceu-nonprd-shared-01` | `eu-central-1` |
| Production | `eks-ceu-prd-shared-01` | `eu-central-1` |

### IAM Roles

The pipelines use OIDC-based authentication with these IAM roles:

- **ECR Push Role**: `arn:aws:iam::{{ AWS_ECR_ACCOUNT_ID }}:role/Terraform`
- **Secrets Manager Role**: `arn:aws:iam::{{ AWS_SECRETS_ACCOUNT_ID }}:role/Terraform-Deploy`
- **EKS Deploy Role (non-prod)**: `arn:aws:iam::{{ AWS_NONPRD_ACCOUNT_ID }}:role/Terraform-Deploy`
- **EKS Deploy Role (prod)**: `arn:aws:iam::{{ AWS_PRD_ACCOUNT_ID }}:role/Terraform-Deploy`

### Kong Control Planes

| Environment | Control Plane |
|-------------|---------------|
| dev | `cp-dev-pub-01` |
| prd | `cp-prd-pub-01` |

---

## Checkov Security Checks

The validation pipeline runs Checkov security scanning on Helm charts. The following checks are skipped by default:

```
CKV_K8S_28,CKV_K8S_37,CKV_K8S_21,CKV_K8S_14,CKV_K8S_43,CKV_K8S_8,CKV_K8S_31,CKV_K8S_40,CKV_K8S_38,CKV_K8S_9,CKV_K8S_20,CKV_K8S_23,CKV_K8S_22,CKV_K8S_35,CKV_K8S_153
```

### Dockle Checks

The following Dockle checks are ignored by default:

```
CIS-DI-0010,DKL-DI-0004
```

These are platform-level decisions. Do not modify the skip lists without consulting the Platform Engineering team.
