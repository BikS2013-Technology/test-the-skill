# Google Cloud Project Management Through Scripting

This guide provides comprehensive instructions for creating Google Cloud projects and managing API services programmatically using both the gcloud CLI and Python SDK.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Creating Projects via gcloud CLI](#creating-projects-via-gcloud-cli)
3. [Enabling APIs via gcloud CLI](#enabling-apis-via-gcloud-cli)
4. [Linking Billing Accounts](#linking-billing-accounts)
5. [Python SDK Implementation](#python-sdk-implementation)
6. [Complete Automation Scripts](#complete-automation-scripts)
7. [Common API Service Names](#common-api-service-names)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Install Google Cloud SDK

```bash
# macOS (using Homebrew)
brew install --cask google-cloud-sdk

# Linux (Debian/Ubuntu)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify installation
gcloud version
```

### 2. Authenticate with Google Cloud

```bash
# Interactive login (for user accounts)
gcloud auth login

# For service accounts (automation)
gcloud auth activate-service-account --key-file=[KEY_FILE_PATH]

# Set up Application Default Credentials (for Python SDK)
gcloud auth application-default login
```

### 3. Required IAM Permissions

To create projects and enable APIs, the authenticated account needs:

- **Project Creator** (`roles/resourcemanager.projectCreator`) - at organization or folder level
- **Service Usage Admin** (`roles/serviceusage.serviceUsageAdmin`) - to enable/disable APIs
- **Billing Account User** (`roles/billing.user`) - to link billing accounts

---

## Creating Projects via gcloud CLI

### Basic Project Creation

```bash
# Basic syntax
gcloud projects create PROJECT_ID

# Example
gcloud projects create my-new-project-2025
```

### Project ID Requirements

- Must start with a lowercase letter
- Can only contain ASCII letters, digits, and hyphens
- Must be between 6 and 30 characters
- Cannot use restricted words: `google`, `null`, `undefined`, `ssl`

### Advanced Project Creation Options

```bash
# Create project with a display name
gcloud projects create my-project-id --name="My Project Display Name"

# Create project under an organization
gcloud projects create my-project-id --organization=ORGANIZATION_ID

# Create project under a folder
gcloud projects create my-project-id --folder=FOLDER_ID

# Create project with labels
gcloud projects create my-project-id --labels=environment=production,team=engineering

# Non-interactive mode (for scripts)
gcloud projects create my-project-id --quiet

# Set the newly created project as default
gcloud projects create my-project-id --set-as-default
```

### Verify Project Creation

```bash
# List all projects
gcloud projects list

# Describe specific project
gcloud projects describe PROJECT_ID

# List projects with formatting
gcloud projects list --format="table(projectNumber,projectId,createTime.date(tz=LOCAL))"
```

---

## Enabling APIs via gcloud CLI

### Enable Single API

```bash
# Basic syntax
gcloud services enable SERVICE_NAME

# Example: Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable for a specific project
gcloud services enable storage.googleapis.com --project=PROJECT_ID
```

### Enable Multiple APIs

```bash
# Enable multiple APIs in sequence
gcloud services enable \
    compute.googleapis.com \
    storage.googleapis.com \
    bigquery.googleapis.com \
    --project=PROJECT_ID

# Or enable individually (can be parallelized)
gcloud services enable compute.googleapis.com --project=PROJECT_ID &
gcloud services enable storage.googleapis.com --project=PROJECT_ID &
gcloud services enable bigquery.googleapis.com --project=PROJECT_ID &
wait
```

### Disable APIs

```bash
# Disable a single API
gcloud services disable SERVICE_NAME --project=PROJECT_ID

# Force disable (ignores dependent services warning)
gcloud services disable SERVICE_NAME --force --project=PROJECT_ID
```

**Important**: Disabling a service does not delete underlying data. You must manually delete resources before disabling to avoid continued charges.

### List and Verify APIs

```bash
# List all enabled APIs for a project
gcloud services list --enabled --project=PROJECT_ID

# List all available APIs
gcloud services list --available --project=PROJECT_ID

# Check if specific API is enabled
gcloud services list --enabled --filter="name:storage.googleapis.com" --project=PROJECT_ID
```

### Check Operation Status

API enable/disable operations are asynchronous. To check status:

```bash
# Get operation details
gcloud services operations describe OPERATION_NAME

# Wait for operation to complete
gcloud services operations wait OPERATION_NAME
```

---

## Linking Billing Accounts

### Prerequisites

- You must have the **Billing Account User** role on the billing account
- The project must exist before linking

### List Available Billing Accounts

```bash
gcloud billing accounts list
```

### Link Project to Billing Account

```bash
# Basic syntax
gcloud billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT_ID

# Example
gcloud billing projects link my-project-id --billing-account=0X0X0X-0X0X0X-0X0X0X
```

### Verify Billing Link

```bash
# Check billing info for a project
gcloud billing projects describe PROJECT_ID

# List all projects linked to a billing account
gcloud billing projects list --billing-account=BILLING_ACCOUNT_ID
```

### Unlink Billing Account

```bash
gcloud billing projects unlink PROJECT_ID
```

---

## Python SDK Implementation

### Installation

Using UV (as per your environment setup):

```bash
# Create virtual environment and install packages
uv venv
source .venv/bin/activate
uv add google-cloud-resource-manager google-cloud-service-usage google-cloud-billing
```

### Creating Projects with Python

```python
"""
Google Cloud Project Creation using Python SDK

Requirements:
    uv add google-cloud-resource-manager
"""

from google.cloud import resourcemanager_v3
from google.cloud.resourcemanager_v3 import Project, CreateProjectRequest
from google.api_core.operation import Operation


def create_project(
    project_id: str,
    display_name: str,
    parent: str = None,
    labels: dict = None
) -> Project:
    """
    Create a new Google Cloud project.

    Args:
        project_id: Unique project identifier (6-30 chars, lowercase letters, digits, hyphens)
        display_name: Human-readable project name
        parent: Optional parent resource (format: 'organizations/ORG_ID' or 'folders/FOLDER_ID')
        labels: Optional dictionary of labels

    Returns:
        Created Project object

    Raises:
        google.api_core.exceptions.AlreadyExists: If project ID already exists
        google.api_core.exceptions.InvalidArgument: If project ID is invalid
    """
    client = resourcemanager_v3.ProjectsClient()

    # Build the project object
    project = Project(
        project_id=project_id,
        display_name=display_name,
    )

    if parent:
        project.parent = parent

    if labels:
        project.labels = labels

    # Create the request
    request = CreateProjectRequest(project=project)

    # Execute the request (returns a long-running operation)
    operation: Operation = client.create_project(request=request)

    # Wait for the operation to complete
    print(f"Creating project '{project_id}'...")
    result = operation.result()

    print(f"Project created successfully: {result.name}")
    return result


def list_projects(parent: str = None) -> list:
    """
    List all accessible projects.

    Args:
        parent: Optional parent to filter by (organization or folder)

    Returns:
        List of Project objects
    """
    client = resourcemanager_v3.ProjectsClient()

    request = resourcemanager_v3.ListProjectsRequest(parent=parent or "")

    projects = []
    for project in client.list_projects(request=request):
        projects.append(project)
        print(f"- {project.project_id}: {project.display_name}")

    return projects


def delete_project(project_id: str) -> None:
    """
    Delete a Google Cloud project.

    Note: Projects are not immediately deleted but enter a 30-day recovery period.

    Args:
        project_id: The project ID to delete
    """
    client = resourcemanager_v3.ProjectsClient()

    request = resourcemanager_v3.DeleteProjectRequest(
        name=f"projects/{project_id}"
    )

    operation = client.delete_project(request=request)
    operation.result()

    print(f"Project '{project_id}' scheduled for deletion.")


# Example usage
if __name__ == "__main__":
    # Create a new project
    new_project = create_project(
        project_id="my-automated-project-123",
        display_name="My Automated Project",
        labels={"environment": "development", "team": "platform"}
    )

    # List all projects
    print("\nAll accessible projects:")
    list_projects()
```

### Enabling APIs with Python

```python
"""
Google Cloud API Service Management using Python SDK

Requirements:
    uv add google-cloud-service-usage
"""

from google.cloud import service_usage_v1
from google.cloud.service_usage_v1 import (
    EnableServiceRequest,
    DisableServiceRequest,
    BatchEnableServicesRequest,
    ListServicesRequest,
    Service,
)


def enable_api(project_id: str, service_name: str) -> Service:
    """
    Enable a single API service for a project.

    Args:
        project_id: The Google Cloud project ID
        service_name: The API service name (e.g., 'storage.googleapis.com')

    Returns:
        The enabled Service object
    """
    client = service_usage_v1.ServiceUsageClient()

    # Format the service resource name
    name = f"projects/{project_id}/services/{service_name}"

    request = EnableServiceRequest(name=name)

    print(f"Enabling {service_name} for project {project_id}...")
    operation = client.enable_service(request=request)

    # Wait for completion
    response = operation.result()

    print(f"Service {service_name} enabled successfully.")
    return response.service


def enable_multiple_apis(project_id: str, service_names: list) -> list:
    """
    Enable multiple API services at once (batch operation).

    Args:
        project_id: The Google Cloud project ID
        service_names: List of API service names

    Returns:
        List of enabled Service objects
    """
    client = service_usage_v1.ServiceUsageClient()

    # Format the parent resource
    parent = f"projects/{project_id}"

    request = BatchEnableServicesRequest(
        parent=parent,
        service_ids=service_names
    )

    print(f"Enabling {len(service_names)} services for project {project_id}...")
    operation = client.batch_enable_services(request=request)

    # Wait for completion
    response = operation.result()

    print(f"All services enabled successfully.")
    return list(response.services)


def disable_api(project_id: str, service_name: str, force: bool = False) -> None:
    """
    Disable an API service for a project.

    Args:
        project_id: The Google Cloud project ID
        service_name: The API service name
        force: If True, disable even if other services depend on it
    """
    client = service_usage_v1.ServiceUsageClient()

    name = f"projects/{project_id}/services/{service_name}"

    request = DisableServiceRequest(
        name=name,
        disable_dependent_services=force
    )

    print(f"Disabling {service_name} for project {project_id}...")
    operation = client.disable_service(request=request)
    operation.result()

    print(f"Service {service_name} disabled.")


def list_enabled_apis(project_id: str) -> list:
    """
    List all enabled APIs for a project.

    Args:
        project_id: The Google Cloud project ID

    Returns:
        List of enabled Service objects
    """
    client = service_usage_v1.ServiceUsageClient()

    request = ListServicesRequest(
        parent=f"projects/{project_id}",
        filter="state:ENABLED"
    )

    services = []
    print(f"Enabled APIs for project {project_id}:")
    for service in client.list_services(request=request):
        services.append(service)
        print(f"  - {service.config.name}: {service.config.title}")

    return services


# Example usage
if __name__ == "__main__":
    PROJECT_ID = "my-project-id"

    # Enable single API
    enable_api(PROJECT_ID, "storage.googleapis.com")

    # Enable multiple APIs at once
    apis_to_enable = [
        "compute.googleapis.com",
        "bigquery.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "iam.googleapis.com",
    ]
    enable_multiple_apis(PROJECT_ID, apis_to_enable)

    # List all enabled APIs
    list_enabled_apis(PROJECT_ID)
```

### Linking Billing Accounts with Python

```python
"""
Google Cloud Billing Management using Python SDK

Requirements:
    uv add google-cloud-billing
"""

from google.cloud import billing_v1
from google.cloud.billing_v1 import (
    ProjectBillingInfo,
    UpdateProjectBillingInfoRequest,
    GetProjectBillingInfoRequest,
)


def link_billing_account(project_id: str, billing_account_id: str) -> ProjectBillingInfo:
    """
    Link a project to a billing account.

    Args:
        project_id: The Google Cloud project ID
        billing_account_id: The billing account ID (format: XXXXXX-XXXXXX-XXXXXX)

    Returns:
        Updated ProjectBillingInfo object
    """
    client = billing_v1.CloudBillingClient()

    # Format the billing account name
    billing_account_name = f"billingAccounts/{billing_account_id}"

    # Create the billing info object
    billing_info = ProjectBillingInfo(
        name=f"projects/{project_id}/billingInfo",
        billing_account_name=billing_account_name
    )

    request = UpdateProjectBillingInfoRequest(
        name=f"projects/{project_id}/billingInfo",
        project_billing_info=billing_info
    )

    print(f"Linking project {project_id} to billing account {billing_account_id}...")
    result = client.update_project_billing_info(request=request)

    print(f"Billing account linked successfully.")
    return result


def get_billing_info(project_id: str) -> ProjectBillingInfo:
    """
    Get billing information for a project.

    Args:
        project_id: The Google Cloud project ID

    Returns:
        ProjectBillingInfo object
    """
    client = billing_v1.CloudBillingClient()

    request = GetProjectBillingInfoRequest(
        name=f"projects/{project_id}/billingInfo"
    )

    result = client.get_project_billing_info(request=request)

    print(f"Billing info for {project_id}:")
    print(f"  Billing Account: {result.billing_account_name}")
    print(f"  Billing Enabled: {result.billing_enabled}")

    return result


def list_billing_accounts() -> list:
    """
    List all accessible billing accounts.

    Returns:
        List of BillingAccount objects
    """
    client = billing_v1.CloudBillingClient()

    accounts = []
    print("Available billing accounts:")
    for account in client.list_billing_accounts():
        accounts.append(account)
        print(f"  - {account.name}: {account.display_name}")

    return accounts


# Example usage
if __name__ == "__main__":
    # List available billing accounts
    accounts = list_billing_accounts()

    # Link a project to a billing account
    if accounts:
        billing_id = accounts[0].name.split("/")[-1]  # Extract ID from name
        link_billing_account("my-project-id", billing_id)

    # Get billing info
    get_billing_info("my-project-id")
```

---

## Complete Automation Scripts

### Bash Script: Full Project Setup

```bash
#!/bin/bash
#
# Complete Google Cloud Project Setup Script
# Creates a project, links billing, and enables required APIs
#

set -e  # Exit on error

# Configuration
PROJECT_ID="${1:-my-new-project-$(date +%Y%m%d)}"
DISPLAY_NAME="${2:-My Automated Project}"
BILLING_ACCOUNT="${3}"  # Required
ORGANIZATION_ID="${4}"  # Optional

# APIs to enable
APIS=(
    "cloudresourcemanager.googleapis.com"
    "serviceusage.googleapis.com"
    "iam.googleapis.com"
    "compute.googleapis.com"
    "storage.googleapis.com"
)

echo "========================================"
echo "Google Cloud Project Setup"
echo "========================================"
echo "Project ID: ${PROJECT_ID}"
echo "Display Name: ${DISPLAY_NAME}"
echo "Billing Account: ${BILLING_ACCOUNT}"
echo "========================================"

# Validate billing account is provided
if [ -z "${BILLING_ACCOUNT}" ]; then
    echo "ERROR: Billing account ID is required."
    echo "Usage: $0 <project-id> <display-name> <billing-account-id> [organization-id]"
    exit 1
fi

# Step 1: Create the project
echo ""
echo "Step 1: Creating project..."
if [ -n "${ORGANIZATION_ID}" ]; then
    gcloud projects create "${PROJECT_ID}" \
        --name="${DISPLAY_NAME}" \
        --organization="${ORGANIZATION_ID}" \
        --quiet
else
    gcloud projects create "${PROJECT_ID}" \
        --name="${DISPLAY_NAME}" \
        --quiet
fi
echo "Project created successfully."

# Step 2: Link billing account
echo ""
echo "Step 2: Linking billing account..."
gcloud billing projects link "${PROJECT_ID}" \
    --billing-account="${BILLING_ACCOUNT}" \
    --quiet
echo "Billing account linked successfully."

# Step 3: Enable APIs
echo ""
echo "Step 3: Enabling APIs..."
for api in "${APIS[@]}"; do
    echo "  Enabling ${api}..."
    gcloud services enable "${api}" \
        --project="${PROJECT_ID}" \
        --quiet
done
echo "All APIs enabled successfully."

# Step 4: Verify setup
echo ""
echo "Step 4: Verifying setup..."
echo ""
echo "Project Details:"
gcloud projects describe "${PROJECT_ID}" --format="yaml(projectId,name,projectNumber,createTime)"

echo ""
echo "Billing Status:"
gcloud billing projects describe "${PROJECT_ID}"

echo ""
echo "Enabled APIs:"
gcloud services list --enabled --project="${PROJECT_ID}" --format="table(config.name,config.title)"

echo ""
echo "========================================"
echo "Project setup completed successfully!"
echo "========================================"
```

### Python Script: Full Project Setup

```python
#!/usr/bin/env python3
"""
Complete Google Cloud Project Setup Script

Creates a project, links billing, and enables required APIs.

Requirements:
    uv add google-cloud-resource-manager google-cloud-service-usage google-cloud-billing

Usage:
    python setup_gcp_project.py --project-id=my-project --billing-account=XXXXXX-XXXXXX-XXXXXX
"""

import argparse
import sys
from datetime import datetime

from google.cloud import resourcemanager_v3
from google.cloud import service_usage_v1
from google.cloud import billing_v1
from google.api_core import exceptions


# Default APIs to enable for new projects
DEFAULT_APIS = [
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "iam.googleapis.com",
    "compute.googleapis.com",
    "storage.googleapis.com",
]


class GCPProjectSetup:
    """Handles complete GCP project setup."""

    def __init__(self, project_id: str, display_name: str, billing_account: str):
        self.project_id = project_id
        self.display_name = display_name
        self.billing_account = billing_account

        # Initialize clients
        self.projects_client = resourcemanager_v3.ProjectsClient()
        self.service_usage_client = service_usage_v1.ServiceUsageClient()
        self.billing_client = billing_v1.CloudBillingClient()

    def create_project(self, parent: str = None, labels: dict = None) -> bool:
        """Create a new GCP project."""
        print(f"\n[1/3] Creating project '{self.project_id}'...")

        try:
            project = resourcemanager_v3.Project(
                project_id=self.project_id,
                display_name=self.display_name,
            )

            if parent:
                project.parent = parent

            if labels:
                project.labels = labels

            request = resourcemanager_v3.CreateProjectRequest(project=project)
            operation = self.projects_client.create_project(request=request)

            result = operation.result()
            print(f"      Project created: {result.name}")
            return True

        except exceptions.AlreadyExists:
            print(f"      Project '{self.project_id}' already exists. Continuing...")
            return True
        except exceptions.InvalidArgument as e:
            print(f"      ERROR: Invalid project configuration: {e}")
            return False
        except Exception as e:
            print(f"      ERROR: Failed to create project: {e}")
            return False

    def link_billing(self) -> bool:
        """Link billing account to the project."""
        print(f"\n[2/3] Linking billing account '{self.billing_account}'...")

        try:
            billing_info = billing_v1.ProjectBillingInfo(
                name=f"projects/{self.project_id}/billingInfo",
                billing_account_name=f"billingAccounts/{self.billing_account}"
            )

            request = billing_v1.UpdateProjectBillingInfoRequest(
                name=f"projects/{self.project_id}/billingInfo",
                project_billing_info=billing_info
            )

            result = self.billing_client.update_project_billing_info(request=request)
            print(f"      Billing enabled: {result.billing_enabled}")
            return True

        except exceptions.PermissionDenied:
            print(f"      ERROR: Permission denied. Check billing account access.")
            return False
        except Exception as e:
            print(f"      ERROR: Failed to link billing: {e}")
            return False

    def enable_apis(self, apis: list = None) -> bool:
        """Enable APIs for the project."""
        apis = apis or DEFAULT_APIS
        print(f"\n[3/3] Enabling {len(apis)} APIs...")

        try:
            request = service_usage_v1.BatchEnableServicesRequest(
                parent=f"projects/{self.project_id}",
                service_ids=apis
            )

            operation = self.service_usage_client.batch_enable_services(request=request)
            result = operation.result()

            for service in result.services:
                print(f"      Enabled: {service.config.name}")

            return True

        except Exception as e:
            print(f"      ERROR: Failed to enable APIs: {e}")
            # Try enabling individually
            print("      Attempting individual API enablement...")
            success = True
            for api in apis:
                try:
                    name = f"projects/{self.project_id}/services/{api}"
                    request = service_usage_v1.EnableServiceRequest(name=name)
                    operation = self.service_usage_client.enable_service(request=request)
                    operation.result()
                    print(f"      Enabled: {api}")
                except Exception as e2:
                    print(f"      FAILED: {api} - {e2}")
                    success = False
            return success

    def verify_setup(self) -> None:
        """Verify the project setup."""
        print("\n" + "=" * 50)
        print("Setup Verification")
        print("=" * 50)

        # Project info
        try:
            request = resourcemanager_v3.GetProjectRequest(
                name=f"projects/{self.project_id}"
            )
            project = self.projects_client.get_project(request=request)
            print(f"\nProject ID: {project.project_id}")
            print(f"Display Name: {project.display_name}")
            print(f"State: {project.state.name}")
        except Exception as e:
            print(f"Could not retrieve project info: {e}")

        # Billing info
        try:
            request = billing_v1.GetProjectBillingInfoRequest(
                name=f"projects/{self.project_id}/billingInfo"
            )
            billing = self.billing_client.get_project_billing_info(request=request)
            print(f"\nBilling Account: {billing.billing_account_name}")
            print(f"Billing Enabled: {billing.billing_enabled}")
        except Exception as e:
            print(f"Could not retrieve billing info: {e}")

        # Enabled APIs
        try:
            request = service_usage_v1.ListServicesRequest(
                parent=f"projects/{self.project_id}",
                filter="state:ENABLED"
            )
            print("\nEnabled APIs:")
            for service in self.service_usage_client.list_services(request=request):
                print(f"  - {service.config.name}")
        except Exception as e:
            print(f"Could not list APIs: {e}")

    def setup(self, parent: str = None, labels: dict = None, apis: list = None) -> bool:
        """Run complete project setup."""
        print("=" * 50)
        print("Google Cloud Project Setup")
        print("=" * 50)
        print(f"Project ID: {self.project_id}")
        print(f"Display Name: {self.display_name}")
        print(f"Billing Account: {self.billing_account}")

        # Step 1: Create project
        if not self.create_project(parent=parent, labels=labels):
            return False

        # Step 2: Link billing
        if not self.link_billing():
            return False

        # Step 3: Enable APIs
        if not self.enable_apis(apis=apis):
            print("\nWARNING: Some APIs may not have been enabled.")

        # Verify
        self.verify_setup()

        print("\n" + "=" * 50)
        print("Setup completed!")
        print("=" * 50)
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Create and configure a Google Cloud project"
    )
    parser.add_argument(
        "--project-id",
        required=True,
        help="Unique project identifier"
    )
    parser.add_argument(
        "--display-name",
        default=None,
        help="Human-readable project name"
    )
    parser.add_argument(
        "--billing-account",
        required=True,
        help="Billing account ID (format: XXXXXX-XXXXXX-XXXXXX)"
    )
    parser.add_argument(
        "--organization",
        default=None,
        help="Organization ID (optional)"
    )
    parser.add_argument(
        "--folder",
        default=None,
        help="Folder ID (optional)"
    )
    parser.add_argument(
        "--apis",
        nargs="+",
        default=None,
        help="List of APIs to enable (space-separated)"
    )

    args = parser.parse_args()

    # Determine parent
    parent = None
    if args.organization:
        parent = f"organizations/{args.organization}"
    elif args.folder:
        parent = f"folders/{args.folder}"

    # Set display name
    display_name = args.display_name or args.project_id

    # Run setup
    setup = GCPProjectSetup(
        project_id=args.project_id,
        display_name=display_name,
        billing_account=args.billing_account
    )

    success = setup.setup(parent=parent, apis=args.apis)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

---

## Common API Service Names

Here are commonly used Google Cloud API service names:

| Service | API Name |
|---------|----------|
| Cloud Resource Manager | `cloudresourcemanager.googleapis.com` |
| Service Usage | `serviceusage.googleapis.com` |
| IAM | `iam.googleapis.com` |
| Cloud Storage | `storage.googleapis.com` |
| Compute Engine | `compute.googleapis.com` |
| BigQuery | `bigquery.googleapis.com` |
| Cloud SQL | `sqladmin.googleapis.com` |
| Cloud Functions | `cloudfunctions.googleapis.com` |
| Cloud Run | `run.googleapis.com` |
| Pub/Sub | `pubsub.googleapis.com` |
| Cloud Build | `cloudbuild.googleapis.com` |
| Container Registry | `containerregistry.googleapis.com` |
| Kubernetes Engine | `container.googleapis.com` |
| Cloud Logging | `logging.googleapis.com` |
| Cloud Monitoring | `monitoring.googleapis.com` |
| Secret Manager | `secretmanager.googleapis.com` |
| Cloud Firestore | `firestore.googleapis.com` |
| Cloud Datastore | `datastore.googleapis.com` |
| Cloud Spanner | `spanner.googleapis.com` |
| Artifact Registry | `artifactregistry.googleapis.com` |
| Cloud Billing | `cloudbilling.googleapis.com` |

---

## Troubleshooting

### Common Errors

#### 1. Project ID Already Exists

```
ERROR: (gcloud.projects.create) ALREADY_EXISTS: project [project-id] already exists
```

**Solution**: Choose a different, globally unique project ID.

#### 2. Permission Denied Creating Projects

```
ERROR: (gcloud.projects.create) PERMISSION_DENIED: The caller does not have permission
```

**Solution**: Ensure you have the `roles/resourcemanager.projectCreator` role at the organization or folder level.

#### 3. Billing Account Link Failed

```
ERROR: (gcloud.billing.projects.link) PERMISSION_DENIED
```

**Solution**: Ensure you have the `roles/billing.user` role on the billing account.

#### 4. API Enable Rate Limit

```
ERROR: Quota exceeded for quota metric 'Mutate requests'
```

**Solution**: Wait and retry. The default rate limit is 2 QPS for API enable/disable operations.

#### 5. Invalid Project ID

```
ERROR: INVALID_ARGUMENT: Invalid project ID
```

**Solution**: Ensure project ID:
- Starts with a lowercase letter
- Contains only lowercase letters, digits, and hyphens
- Is between 6-30 characters
- Does not contain restricted words (`google`, `null`, `undefined`, `ssl`)

### Debug Commands

```bash
# Check current authentication
gcloud auth list

# Verify project access
gcloud projects describe PROJECT_ID

# Check IAM permissions
gcloud projects get-iam-policy PROJECT_ID

# View detailed API operation logs
gcloud logging read "resource.type=audited_resource" --project=PROJECT_ID --limit=10
```

---

## References

- [Creating and managing projects | Resource Manager](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)
- [gcloud services enable | Google Cloud SDK](https://cloud.google.com/sdk/gcloud/reference/services/enable)
- [Enable and disable services | Service Usage](https://docs.cloud.google.com/service-usage/docs/enable-disable)
- [Python Resource Manager Client](https://docs.cloud.google.com/python/docs/reference/cloudresourcemanager/latest)
- [Google Cloud CLI Cheat Sheet](https://docs.cloud.google.com/sdk/docs/cheatsheet)
- [Scripting gcloud CLI commands](https://docs.cloud.google.com/sdk/docs/scripting-gcloud)

---

*Document created: 2025-12-26*
