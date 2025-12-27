# Google Cloud Service Account Key File Creation Guide

**Date:** December 26, 2025

This guide documents the process of creating Service Account Key files for use in Python scripting scenarios with Google APIs.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create a Service Account](#step-1-create-a-service-account)
4. [Step 2: Assign IAM Roles to the Service Account](#step-2-assign-iam-roles-to-the-service-account)
5. [Step 3: Create a Service Account Key](#step-3-create-a-service-account-key)
6. [Step 4: Use the Key in Python](#step-4-use-the-key-in-python)
7. [Scripting the Entire Process](#scripting-the-entire-process)
8. [Programmatic Key Creation with Python](#programmatic-key-creation-with-python)
9. [Security Best Practices](#security-best-practices)
10. [Key Management Operations](#key-management-operations)

---

## Overview

Service accounts are special Google Cloud accounts that represent applications or compute workloads rather than individual users. They are used for server-to-server communication, where your application needs to access Google APIs without user interaction.

A **Service Account Key** is a JSON file containing:
- Private key data
- Service account email
- Project ID
- Client ID and other metadata

This key file allows your Python scripts to authenticate with Google Cloud APIs.

---

## Prerequisites

### Required Tools

1. **Google Cloud SDK (gcloud CLI)** - Install from https://cloud.google.com/sdk
2. **A Google Cloud Project** with billing enabled
3. **IAM API enabled** in your project

### Required Permissions

To create service accounts and keys, you need one of these roles:
- `roles/iam.serviceAccountAdmin` - Full service account management
- `roles/iam.serviceAccountKeyAdmin` - Manage service account keys only
- `roles/owner` or `roles/editor` - Project-level access

Specific permissions needed:
- `iam.serviceAccounts.create` - To create service accounts
- `iam.serviceAccountKeys.create` - To create keys

### Enable the IAM API

```bash
gcloud services enable iam.googleapis.com
```

---

## Step 1: Create a Service Account

### Using gcloud CLI (Scriptable)

```bash
# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Define service account details
export SA_NAME="my-python-scripts"
export SA_DISPLAY_NAME="Python Scripts Service Account"
export SA_DESCRIPTION="Service account for Python scripting with Google APIs"

# Create the service account
gcloud iam service-accounts create $SA_NAME \
    --display-name="$SA_DISPLAY_NAME" \
    --description="$SA_DESCRIPTION" \
    --project=$PROJECT_ID
```

### Verify Creation

```bash
# List service accounts to verify
gcloud iam service-accounts list --project=$PROJECT_ID

# Get service account email
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Service Account Email: $SA_EMAIL"
```

---

## Step 2: Assign IAM Roles to the Service Account

The service account needs specific roles to access Google Cloud resources. Assign roles based on what APIs your Python scripts will use.

### Common Role Examples

```bash
# Storage Admin (for Cloud Storage access)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

# BigQuery User (for BigQuery access)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/bigquery.user"

# Pub/Sub Publisher (for Pub/Sub access)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/pubsub.publisher"
```

### Assign Multiple Roles with a Script

```bash
# Define roles needed for your application
ROLES=(
    "roles/storage.objectViewer"
    "roles/bigquery.dataViewer"
    "roles/logging.viewer"
)

# Assign each role
for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
    echo "Assigned role: $role"
done
```

---

## Step 3: Create a Service Account Key

### Using gcloud CLI (Scriptable)

```bash
# Define key file location
export KEY_FILE="$HOME/.gcloud/${SA_NAME}-key.json"

# Create directory if it doesn't exist
mkdir -p $(dirname $KEY_FILE)

# Create the service account key
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

echo "Key created at: $KEY_FILE"
```

### Set File Permissions (Security)

```bash
# Restrict key file permissions (Unix/Linux/macOS)
chmod 600 $KEY_FILE
```

### Key Output Format

The generated JSON key file has this structure:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id-here",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "my-python-scripts@your-project-id.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

---

## Step 4: Use the Key in Python

### Method 1: Using Environment Variable (Recommended)

```bash
# Set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$KEY_FILE"
```

Then in Python:

```python
# The google-auth library automatically uses GOOGLE_APPLICATION_CREDENTIALS
import google.auth

credentials, project = google.auth.default()
print(f"Authenticated for project: {project}")
```

### Method 2: Load from File Explicitly

```python
from google.oauth2 import service_account

# Load credentials from the JSON key file
credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account-key.json'
)

# Optionally specify scopes
scopes = ['https://www.googleapis.com/auth/cloud-platform']
scoped_credentials = credentials.with_scopes(scopes)
```

### Method 3: Load from Dictionary

```python
import json
from google.oauth2 import service_account

# Load key file content
with open('path/to/service-account-key.json', 'r') as f:
    service_account_info = json.load(f)

# Create credentials from dictionary
credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)
```

### Complete Example: Using Google Cloud Storage

```python
from google.cloud import storage
from google.oauth2 import service_account

def list_buckets(key_file_path: str, project_id: str):
    """List all buckets in a project using service account authentication."""

    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        key_file_path
    )

    # Create storage client with credentials
    client = storage.Client(
        project=project_id,
        credentials=credentials
    )

    # List buckets
    buckets = list(client.list_buckets())
    for bucket in buckets:
        print(f"Bucket: {bucket.name}")

    return buckets

if __name__ == "__main__":
    list_buckets(
        key_file_path="/path/to/service-account-key.json",
        project_id="your-project-id"
    )
```

### Required Python Packages

```bash
# Using UV package manager
uv add google-auth
uv add google-cloud-storage  # For Cloud Storage
uv add google-api-python-client  # For Discovery-based APIs
uv add google-cloud-iam  # For IAM operations
```

---

## Scripting the Entire Process

Here's a complete bash script that automates the entire service account and key creation process:

```bash
#!/bin/bash
# create-service-account.sh
# Creates a service account and key for Python scripting

set -e  # Exit on error

# Configuration - Modify these values
SA_NAME="${1:-python-api-scripts}"
SA_DISPLAY_NAME="${2:-Python API Scripts}"
ROLES="${3:-roles/storage.objectViewer,roles/bigquery.dataViewer}"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "Error: No project configured. Run 'gcloud config set project PROJECT_ID'"
    exit 1
fi

SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_DIR="$HOME/.gcloud/keys"
KEY_FILE="${KEY_DIR}/${SA_NAME}-${PROJECT_ID}.json"

echo "=== Service Account Creation Script ==="
echo "Project: $PROJECT_ID"
echo "Service Account: $SA_NAME"
echo "Key File: $KEY_FILE"
echo ""

# Step 1: Enable IAM API
echo "[1/5] Enabling IAM API..."
gcloud services enable iam.googleapis.com --quiet

# Step 2: Create Service Account
echo "[2/5] Creating service account..."
if gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID &>/dev/null; then
    echo "  Service account already exists, skipping creation."
else
    gcloud iam service-accounts create $SA_NAME \
        --display-name="$SA_DISPLAY_NAME" \
        --description="Created by automation script for Python API access" \
        --project=$PROJECT_ID
    echo "  Service account created."
fi

# Step 3: Assign Roles
echo "[3/5] Assigning IAM roles..."
IFS=',' read -ra ROLE_ARRAY <<< "$ROLES"
for role in "${ROLE_ARRAY[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
    echo "  Assigned: $role"
done

# Step 4: Create Key Directory
echo "[4/5] Creating key directory..."
mkdir -p $KEY_DIR
chmod 700 $KEY_DIR

# Step 5: Create Key
echo "[5/5] Creating service account key..."
if [ -f "$KEY_FILE" ]; then
    echo "  Warning: Key file already exists at $KEY_FILE"
    read -p "  Overwrite? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "  Skipping key creation."
        exit 0
    fi
fi

gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

chmod 600 $KEY_FILE

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Service Account Email: $SA_EMAIL"
echo "Key File: $KEY_FILE"
echo ""
echo "To use in your shell:"
echo "  export GOOGLE_APPLICATION_CREDENTIALS=\"$KEY_FILE\""
echo ""
echo "To use in Python:"
echo "  from google.oauth2 import service_account"
echo "  credentials = service_account.Credentials.from_service_account_file('$KEY_FILE')"
```

### Usage

```bash
# Make executable
chmod +x create-service-account.sh

# Run with defaults
./create-service-account.sh

# Run with custom name and roles
./create-service-account.sh "my-app-sa" "My Application" "roles/storage.admin,roles/pubsub.admin"
```

---

## Programmatic Key Creation with Python

You can also create service account keys programmatically using Python.

### Method 1: Using google-cloud-iam (Recommended)

```python
"""
Create a service account key programmatically using google-cloud-iam.

Prerequisites:
- uv add google-cloud-iam
- Authenticated with gcloud or have GOOGLE_APPLICATION_CREDENTIALS set
- Have iam.serviceAccountKeys.create permission
"""
import json
from google.cloud import iam_admin_v1
from google.cloud.iam_admin_v1 import types


def create_service_account_key(
    project_id: str,
    service_account_email: str,
    output_file: str
) -> types.ServiceAccountKey:
    """
    Creates a key for a service account and saves it to a file.

    Args:
        project_id: ID of the Google Cloud project
        service_account_email: Email of the service account
        output_file: Path where to save the JSON key file

    Returns:
        ServiceAccountKey object
    """
    # Create IAM client
    iam_client = iam_admin_v1.IAMClient()

    # Build the request
    request = types.CreateServiceAccountKeyRequest()
    request.name = f"projects/{project_id}/serviceAccounts/{service_account_email}"

    # Create the key
    key = iam_client.create_service_account_key(request=request)

    # The private_key_data contains the base64-encoded JSON key
    # Decode and save to file
    import base64
    key_data = base64.b64decode(key.private_key_data).decode('utf-8')

    with open(output_file, 'w') as f:
        f.write(key_data)

    print(f"Key created and saved to: {output_file}")
    print(f"Key ID: {key.name.split('/')[-1]}")

    return key


if __name__ == "__main__":
    create_service_account_key(
        project_id="your-project-id",
        service_account_email="your-sa@your-project-id.iam.gserviceaccount.com",
        output_file="./new-service-account-key.json"
    )
```

### Method 2: Using google-api-python-client

```python
"""
Create a service account key using the Google API Python Client.

Prerequisites:
- uv add google-api-python-client google-auth
- Authenticated with Application Default Credentials
"""
import json
import base64
from googleapiclient import discovery
from google.oauth2 import service_account
import google.auth


def create_key_with_api_client(
    service_account_email: str,
    output_file: str,
    project_id: str = None
) -> dict:
    """
    Creates a service account key using the IAM API.

    Args:
        service_account_email: Email of the service account
        output_file: Path to save the JSON key
        project_id: Optional project ID (uses '-' wildcard if not specified)

    Returns:
        The API response dictionary
    """
    # Get default credentials
    credentials, default_project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )

    # Build IAM service
    service = discovery.build('iam', 'v1', credentials=credentials)

    # Build resource name
    if project_id:
        name = f'projects/{project_id}/serviceAccounts/{service_account_email}'
    else:
        name = f'projects/-/serviceAccounts/{service_account_email}'

    # Create the key
    request = service.projects().serviceAccounts().keys().create(
        name=name,
        body={}  # Empty body uses defaults (JSON format, RSA 2048)
    )
    response = request.execute()

    # Decode and save the private key data
    private_key_data = base64.b64decode(response['privateKeyData']).decode('utf-8')

    with open(output_file, 'w') as f:
        f.write(private_key_data)

    print(f"Key created successfully!")
    print(f"Key name: {response['name']}")
    print(f"Saved to: {output_file}")

    return response


if __name__ == "__main__":
    create_key_with_api_client(
        service_account_email="my-sa@my-project.iam.gserviceaccount.com",
        output_file="./my-new-key.json"
    )
```

---

## Security Best Practices

### Key Storage

1. **Never commit keys to version control**
   ```gitignore
   # .gitignore
   *.json
   *-key.json
   service-account*.json
   credentials/
   ```

2. **Use secure storage locations**
   ```bash
   # Store in user's home directory with restricted permissions
   mkdir -p ~/.gcloud/keys
   chmod 700 ~/.gcloud/keys
   chmod 600 ~/.gcloud/keys/*.json
   ```

3. **Consider using Secret Manager for production**
   ```python
   from google.cloud import secretmanager

   def get_key_from_secret_manager(project_id: str, secret_id: str) -> dict:
       client = secretmanager.SecretManagerServiceClient()
       name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
       response = client.access_secret_version(request={"name": name})
       return json.loads(response.payload.data.decode('UTF-8'))
   ```

### Key Rotation

1. **List existing keys**
   ```bash
   gcloud iam service-accounts keys list \
       --iam-account=$SA_EMAIL \
       --project=$PROJECT_ID
   ```

2. **Delete old keys**
   ```bash
   gcloud iam service-accounts keys delete KEY_ID \
       --iam-account=$SA_EMAIL \
       --project=$PROJECT_ID
   ```

3. **Automate rotation** - Create new key, update applications, delete old key

### Least Privilege Principle

- Only grant the minimum roles needed
- Use predefined roles instead of primitive roles (Owner, Editor, Viewer)
- Consider custom roles for fine-grained access

### Alternatives to Key Files

For workloads running on Google Cloud, consider:

1. **Workload Identity** (GKE) - No key files needed
2. **Attached Service Accounts** (Compute Engine, Cloud Run) - Automatic credentials
3. **Short-lived credentials** - Use `iam.serviceAccountTokenCreator` role

---

## Key Management Operations

### List Keys

```bash
gcloud iam service-accounts keys list \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID
```

### Delete a Key

```bash
gcloud iam service-accounts keys delete KEY_ID \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID
```

### Delete Key with Python

```python
from google.cloud import iam_admin_v1
from google.cloud.iam_admin_v1 import types


def delete_service_account_key(
    project_id: str,
    service_account_email: str,
    key_id: str
) -> None:
    """Deletes a service account key."""
    iam_client = iam_admin_v1.IAMClient()

    request = types.DeleteServiceAccountKeyRequest()
    request.name = f"projects/{project_id}/serviceAccounts/{service_account_email}/keys/{key_id}"

    iam_client.delete_service_account_key(request=request)
    print(f"Deleted key: {key_id}")
```

### Disable/Enable a Service Account

```bash
# Disable
gcloud iam service-accounts disable $SA_EMAIL --project=$PROJECT_ID

# Enable
gcloud iam service-accounts enable $SA_EMAIL --project=$PROJECT_ID
```

---

## Summary

| Step | Method | Scriptable |
|------|--------|------------|
| Enable IAM API | `gcloud services enable` | Yes |
| Create Service Account | `gcloud iam service-accounts create` | Yes |
| Assign Roles | `gcloud projects add-iam-policy-binding` | Yes |
| Create Key | `gcloud iam service-accounts keys create` | Yes |
| Create Key (Python) | `google-cloud-iam` library | Yes |
| Use Key in Python | `google-auth` / `google.oauth2.service_account` | Yes |

All operations can be fully automated through shell scripts or Python code.

---

## References

### Official Google Cloud Documentation

- [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs)
- [Creating and Deleting Service Account Keys](https://cloud.google.com/iam/docs/keys-create-delete)
- [Best Practices for Managing Service Account Keys](https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys)
- [IAM REST API Reference - Service Account Keys](https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts.keys/create)
- [IAM REST API Reference - Service Accounts](https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts/create)
- [IAM RPC Reference](https://cloud.google.com/iam/docs/reference/rpc/google.iam)
- [Creating Short-Lived Credentials](https://cloud.google.com/iam/docs/create-short-lived-credentials-direct)

### Python Libraries Documentation

- [google-auth Python Library](https://googleapis.dev/python/google-auth/latest/)
- [google-auth Service Account Module](https://googleapis.dev/python/google-auth/latest/reference/google.oauth2.service_account)
- [google-api-python-client IAM Documentation](https://github.com/googleapis/google-api-python-client/blob/main/docs/dyn/iam_v1.projects.serviceAccounts.keys.html)
- [google-cloud-iam-admin Python Library](https://cloud.google.com/python/docs/reference/iam/latest)

### Google Cloud SDK (gcloud CLI)

- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [gcloud iam service-accounts](https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts)

### Code Samples

- [Google Cloud Platform Python Docs Samples](https://github.com/googlecloudplatform/python-docs-samples)

---

## Sources Used in This Document

This document was compiled using documentation retrieved via the Context7 plugin from the following sources:

| Source | Context7 Library ID | Content Used |
|--------|---------------------|--------------|
| Google Cloud IAM | `/websites/cloud_google_iam` | Service account creation, key creation API, permissions |
| google-auth Python | `/websites/googleapis_dev_python_google-auth` | Service account credentials, authentication methods |
| GCP Python Samples | `/googlecloudplatform/python-docs-samples` | Practical examples, gcloud commands |
| Google API Python Client | `/googleapis/google-api-python-client` | IAM API usage, key creation |
| gcloud CLI Reference | `/websites/cloud_google_sdk_gcloud_reference` | CLI commands and flags |

**Document Generated:** December 26, 2025
