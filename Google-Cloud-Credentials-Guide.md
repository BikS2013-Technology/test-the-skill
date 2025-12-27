# Google Cloud Credentials.json Creation Guide

## Overview

This guide explains how to create `credentials.json` files for Google Cloud services, identifying which steps can be automated via scripts and which require manual configuration through the Google Cloud Console.

There are two main types of credentials:
1. **Service Account Keys** - For application-to-application authentication (fully scriptable)
2. **OAuth 2.0 Client IDs** - For user authentication with consent flows (partially manual)

---

## Manual vs Scriptable Steps

### Steps That CANNOT Be Scripted

| Step | Reason | Where to Do It |
|------|--------|----------------|
| Google Cloud account creation | Requires email verification and agreement to terms | [Google Cloud Console](https://console.cloud.google.com) |
| Initial billing account creation | Requires payment method verification | Google Cloud Console > Billing |
| OAuth consent screen configuration | Requires interactive form with app details, logos, scopes | Google Cloud Console > APIs & Services > OAuth consent screen |
| OAuth 2.0 Client ID creation | No gcloud CLI equivalent exists | Google Cloud Console > APIs & Services > Credentials |
| Domain-wide delegation authorization | Requires Google Admin Console access | [Google Admin Console](https://admin.google.com) |

### Steps That CAN Be Scripted

| Step | Command | Notes |
|------|---------|-------|
| Project creation | `gcloud projects create` | Requires organization/folder permissions |
| Link billing account | `gcloud beta billing projects link` | Billing account must already exist |
| Enable APIs | `gcloud services enable` | Can enable multiple APIs |
| Create service account | `gcloud iam service-accounts create` | Generates email automatically |
| Assign IAM roles | `gcloud projects add-iam-policy-binding` | Multiple roles can be assigned |
| Generate service account key | `gcloud iam service-accounts keys create` | Downloads credentials.json |

---

## Prerequisites

Before running any scripts, ensure you have:

1. **Google Cloud SDK (gcloud CLI) installed**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk

   # Or download from https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticated with gcloud**
   ```bash
   gcloud auth login
   ```

3. **A billing account** (create manually in Google Cloud Console if not exists)
   - List existing billing accounts:
     ```bash
     gcloud beta billing accounts list
     ```

---

## Service Account Credentials (Fully Scriptable)

Service accounts are ideal for server-to-server authentication, CI/CD pipelines, and automated scripts.

### Complete Script for Single API

```bash
#!/bin/bash
# create-service-account-credentials.sh
# Creates a service account with credentials.json for a single API

set -e  # Exit on error

# Configuration - MODIFY THESE VALUES
PROJECT_ID="my-project-id"
SERVICE_ACCOUNT_NAME="my-service-account"
DISPLAY_NAME="My Service Account"
DESCRIPTION="Service account for API access"
KEY_FILE="./credentials.json"
API_TO_ENABLE="sheets.googleapis.com"  # Example: Google Sheets API
# WARNING: roles/editor is overly broad for production use.
# See Security Best Practices section for recommended specific roles.
ROLE="roles/editor"  # Adjust based on needs

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=== Google Cloud Service Account Setup ==="

# Step 1: Set the project
echo -e "\n${GREEN}[1/6]${NC} Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Step 2: Enable the API
echo -e "\n${GREEN}[2/6]${NC} Enabling ${API_TO_ENABLE}..."
gcloud services enable ${API_TO_ENABLE}

# Step 3: Create the service account
echo -e "\n${GREEN}[3/6]${NC} Creating service account ${SERVICE_ACCOUNT_NAME}..."
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --description="${DESCRIPTION}" \
    --display-name="${DISPLAY_NAME}" \
    2>/dev/null || echo "Service account may already exist, continuing..."

# Step 4: Get the full service account email
SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo -e "\n${GREEN}[4/6]${NC} Service account email: ${SA_EMAIL}"

# Step 5: Grant IAM role to the service account
echo -e "\n${GREEN}[5/6]${NC} Granting ${ROLE} role..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" \
    --quiet

# Step 6: Generate the credentials.json key file
echo -e "\n${GREEN}[6/6]${NC} Generating credentials.json..."
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SA_EMAIL}

echo -e "\n${GREEN}=== Setup Complete ===${NC}"
echo "Credentials saved to: ${KEY_FILE}"
echo ""
echo "IMPORTANT: Store this file securely!"
echo "          - Add to .gitignore"
echo "          - Never commit to version control"
echo "          - Cannot be downloaded again if lost"
```

### Script for Multiple APIs

```bash
#!/bin/bash
# create-multi-api-credentials.sh
# Creates a service account with access to multiple APIs

set -e

# Configuration
PROJECT_ID="my-project-id"
SERVICE_ACCOUNT_NAME="multi-api-service-account"
DISPLAY_NAME="Multi-API Service Account"
KEY_FILE="./credentials.json"

# List of APIs to enable
APIS=(
    "sheets.googleapis.com"
    "drive.googleapis.com"
    "gmail.googleapis.com"
    "calendar-json.googleapis.com"
    "docs.googleapis.com"
)

# Roles to assign (add roles as needed per API requirements)
ROLES=(
    "roles/editor"
)

echo "=== Multi-API Service Account Setup ==="

# Set project
gcloud config set project ${PROJECT_ID}

# Enable all APIs
echo -e "\nEnabling APIs..."
for api in "${APIS[@]}"; do
    echo "  - Enabling ${api}..."
    gcloud services enable ${api}
done

# Create service account
echo -e "\nCreating service account..."
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="${DISPLAY_NAME}" \
    2>/dev/null || echo "Service account may already exist"

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Assign all roles
echo -e "\nAssigning roles..."
for role in "${ROLES[@]}"; do
    echo "  - Granting ${role}..."
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="${role}" \
        --quiet
done

# Generate key
echo -e "\nGenerating credentials.json..."
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SA_EMAIL}

echo -e "\n=== Setup Complete ==="
echo "Enabled APIs: ${#APIS[@]}"
echo "Credentials: ${KEY_FILE}"
```

### Script for Multiple Services/Projects

```bash
#!/bin/bash
# create-multi-service-credentials.sh
# Creates service accounts across multiple projects/services

set -e

# Define services configuration
# Format: "project_id:service_account_name:api_list:output_file"
SERVICES=(
    "project-a:sheets-sa:sheets.googleapis.com,drive.googleapis.com:./creds-sheets.json"
    "project-b:vision-sa:vision.googleapis.com:./creds-vision.json"
    "project-c:translate-sa:translate.googleapis.com:./creds-translate.json"
)

create_service_account() {
    local project_id=$1
    local sa_name=$2
    local apis=$3
    local output_file=$4

    echo "=== Setting up ${sa_name} in ${project_id} ==="

    # Set project
    gcloud config set project ${project_id}

    # Enable APIs (split by comma)
    IFS=',' read -ra API_ARRAY <<< "$apis"
    for api in "${API_ARRAY[@]}"; do
        echo "  Enabling ${api}..."
        gcloud services enable ${api} 2>/dev/null || true
    done

    # Create service account
    gcloud iam service-accounts create ${sa_name} \
        --display-name="${sa_name}" \
        2>/dev/null || echo "  Service account exists"

    local sa_email="${sa_name}@${project_id}.iam.gserviceaccount.com"

    # Grant editor role
    gcloud projects add-iam-policy-binding ${project_id} \
        --member="serviceAccount:${sa_email}" \
        --role="roles/editor" \
        --quiet

    # Generate key
    gcloud iam service-accounts keys create ${output_file} \
        --iam-account=${sa_email}

    echo "  Credentials saved to: ${output_file}"
    echo ""
}

# Process each service
for service in "${SERVICES[@]}"; do
    IFS=':' read -r project sa apis output <<< "$service"
    create_service_account "$project" "$sa" "$apis" "$output"
done

echo "=== All service accounts created ==="
```

---

## Complete Project Setup Script

This script handles the entire setup from project creation to credentials generation:

```bash
#!/bin/bash
# complete-project-setup.sh
# Complete Google Cloud project setup with service account credentials

set -e

# Configuration
PROJECT_ID="my-new-project-$(date +%Y%m%d)"
BILLING_ACCOUNT_ID=""  # Set this! Get from: gcloud beta billing accounts list
SERVICE_ACCOUNT_NAME="app-service-account"
KEY_FILE="./credentials.json"
ORGANIZATION_ID=""  # Optional: your organization ID

# APIs to enable
APIS=(
    "iam.googleapis.com"
    "iamcredentials.googleapis.com"
    # Add more APIs as needed
)

echo "=== Complete Google Cloud Project Setup ==="

# Validate billing account is set
if [ -z "$BILLING_ACCOUNT_ID" ]; then
    echo "ERROR: BILLING_ACCOUNT_ID not set"
    echo "Get your billing account ID with: gcloud beta billing accounts list"
    exit 1
fi

# Step 1: Create project
echo -e "\n[1/6] Creating project ${PROJECT_ID}..."
if [ -n "$ORGANIZATION_ID" ]; then
    gcloud projects create ${PROJECT_ID} --organization=${ORGANIZATION_ID}
else
    gcloud projects create ${PROJECT_ID}
fi

# Step 2: Link billing account
echo -e "\n[2/6] Linking billing account..."
gcloud beta billing projects link ${PROJECT_ID} \
    --billing-account=${BILLING_ACCOUNT_ID}

# Step 3: Set as current project
echo -e "\n[3/6] Setting as current project..."
gcloud config set project ${PROJECT_ID}

# Step 4: Enable APIs
echo -e "\n[4/6] Enabling APIs..."
for api in "${APIS[@]}"; do
    echo "  - ${api}"
    gcloud services enable ${api}
done

# Step 5: Create service account
echo -e "\n[5/6] Creating service account..."
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="Application Service Account"

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/editor" \
    --quiet

# Step 6: Generate credentials
echo -e "\n[6/6] Generating credentials..."
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SA_EMAIL}

echo -e "\n=== Setup Complete ==="
echo "Project ID: ${PROJECT_ID}"
echo "Service Account: ${SA_EMAIL}"
echo "Credentials: ${KEY_FILE}"
echo ""
echo "Next steps:"
echo "  1. Add ${KEY_FILE} to .gitignore"
echo "  2. Set environment variable: export GOOGLE_APPLICATION_CREDENTIALS=${KEY_FILE}"
```

---

## OAuth 2.0 Client Credentials (Partially Manual)

For applications requiring user consent (accessing user's Drive, Gmail, etc.), you need OAuth 2.0 Client IDs. This process requires manual steps in the Google Cloud Console.

### Manual Steps Required

1. **Configure OAuth Consent Screen**
   - Go to: Google Cloud Console > APIs & Services > OAuth consent screen
   - Select user type (Internal/External)
   - Fill in application name, support email, and developer contact
   - Add required scopes
   - Add test users (if external)

2. **Create OAuth Client ID**
   - Go to: Google Cloud Console > APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Select application type:
     - **Web application**: For server-side apps
     - **Desktop app**: For CLI tools
     - **Android/iOS**: For mobile apps
   - Configure authorized redirect URIs
   - Download the JSON file as `credentials.json`

### Script to Prepare for OAuth

While you can't create OAuth Client IDs via script, you can automate the API enablement:

```bash
#!/bin/bash
# prepare-oauth-project.sh
# Prepares a project for OAuth credentials (manual OAuth setup still required)

set -e  # Exit on error

PROJECT_ID="my-project-id"

OAUTH_APIS=(
    "oauth2.googleapis.com"
    "people.googleapis.com"  # For user info
    # Add APIs your OAuth app will use
    "drive.googleapis.com"
    "gmail.googleapis.com"
)

echo "=== Preparing Project for OAuth ==="

gcloud config set project ${PROJECT_ID}

echo "Enabling OAuth-related APIs..."
for api in "${OAUTH_APIS[@]}"; do
    echo "  - ${api}"
    gcloud services enable ${api}
done

echo ""
echo "=== Manual Steps Required ==="
echo "1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=${PROJECT_ID}"
echo "   - Configure OAuth consent screen"
echo ""
echo "2. Go to: https://console.cloud.google.com/apis/credentials?project=${PROJECT_ID}"
echo "   - Click 'Create Credentials' > 'OAuth client ID'"
echo "   - Download credentials.json"
```

---

## Common API Service Names

Reference table for commonly used Google APIs:

| Service | API Name | Description |
|---------|----------|-------------|
| Google Sheets | `sheets.googleapis.com` | Spreadsheet access |
| Google Drive | `drive.googleapis.com` | File storage |
| Gmail | `gmail.googleapis.com` | Email access |
| Google Calendar | `calendar-json.googleapis.com` | Calendar events |
| Google Docs | `docs.googleapis.com` | Document access |
| Cloud Vision | `vision.googleapis.com` | Image analysis |
| Cloud Translation | `translate.googleapis.com` | Text translation |
| Cloud Speech-to-Text | `speech.googleapis.com` | Audio transcription |
| Cloud Text-to-Speech | `texttospeech.googleapis.com` | Speech synthesis |
| Cloud Natural Language | `language.googleapis.com` | Text analysis |
| BigQuery | `bigquery.googleapis.com` | Data analytics |
| Cloud Storage | `storage.googleapis.com` | Object storage |
| Compute Engine | `compute.googleapis.com` | Virtual machines |
| Cloud Functions | `cloudfunctions.googleapis.com` | Serverless functions |
| Cloud Run | `run.googleapis.com` | Container services |
| Kubernetes Engine | `container.googleapis.com` | Kubernetes clusters |
| Cloud SQL | `sqladmin.googleapis.com` | Managed databases |
| Vertex AI | `aiplatform.googleapis.com` | ML platform |
| IAM | `iam.googleapis.com` | Identity management |

---

## Useful gcloud Commands Reference

### Project Management
```bash
# List all projects
gcloud projects list

# Create a project
gcloud projects create PROJECT_ID

# Set current project
gcloud config set project PROJECT_ID

# Get current project
gcloud config get-value project
```

### Billing
```bash
# List billing accounts
gcloud beta billing accounts list

# Link billing to project
gcloud beta billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT_ID

# Check if billing is enabled
gcloud beta billing projects describe PROJECT_ID
```

### Service Accounts
```bash
# List service accounts
gcloud iam service-accounts list

# Create service account
gcloud iam service-accounts create SA_NAME --display-name="Display Name"

# Delete service account
gcloud iam service-accounts delete SA_EMAIL

# List keys for a service account
gcloud iam service-accounts keys list --iam-account=SA_EMAIL
```

### Keys Management
```bash
# Create key (downloads JSON)
gcloud iam service-accounts keys create key.json --iam-account=SA_EMAIL

# Delete a key
gcloud iam service-accounts keys delete KEY_ID --iam-account=SA_EMAIL
```

### APIs/Services
```bash
# List enabled services
gcloud services list --enabled

# List all available services
gcloud services list --available

# Enable a service
gcloud services enable SERVICE_NAME

# Disable a service
gcloud services disable SERVICE_NAME
```

### IAM Roles
```bash
# List roles for a project
gcloud projects get-iam-policy PROJECT_ID

# Grant role
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SA_EMAIL" \
    --role="ROLE_NAME"

# Remove role
gcloud projects remove-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:SA_EMAIL" \
    --role="ROLE_NAME"
```

---

## Security Best Practices

1. **Never commit credentials.json to version control**
   ```bash
   # Add to .gitignore
   echo "credentials.json" >> .gitignore
   echo "*-credentials.json" >> .gitignore  # For named credential files
   echo "service-account-*.json" >> .gitignore  # For service account keys
   # Note: Avoid "*.json" as it ignores legitimate files like package.json
   ```

2. **Use environment variables**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```

3. **Rotate keys regularly**
   ```bash
   # Create new key
   gcloud iam service-accounts keys create new-key.json --iam-account=SA_EMAIL

   # Update application to use new key

   # Delete old key
   gcloud iam service-accounts keys delete OLD_KEY_ID --iam-account=SA_EMAIL
   ```

4. **Use minimal permissions**
   - Grant only the specific roles needed
   - Avoid using `roles/owner` or `roles/editor` in production
   - Use predefined or custom roles with least privilege

5. **Consider alternatives to key files**
   - Workload Identity Federation (for non-GCP environments)
   - Service account impersonation
   - Attached service accounts (for GCP resources)

---

## Troubleshooting

### "Permission denied" when creating service account
```bash
# Check your current permissions
gcloud projects get-iam-policy PROJECT_ID --format="json" | \
    grep -A5 "YOUR_EMAIL"

# You need roles/iam.serviceAccountAdmin or roles/owner
```

### "Billing account not found"
```bash
# List your billing accounts
gcloud beta billing accounts list

# Ensure you have Billing Account User role
```

### "API not enabled"
```bash
# Enable the required API
gcloud services enable API_NAME.googleapis.com

# Verify it's enabled
gcloud services list --enabled | grep API_NAME
```

### Service account key limit reached (max 10)
```bash
# List existing keys
gcloud iam service-accounts keys list --iam-account=SA_EMAIL

# Delete unused keys
gcloud iam service-accounts keys delete KEY_ID --iam-account=SA_EMAIL
```

---

## Summary

| Credential Type | Use Case | Scriptable? | Key Command |
|-----------------|----------|-------------|-------------|
| Service Account Key | Server-to-server, automation | Yes | `gcloud iam service-accounts keys create` |
| OAuth Client ID | User authentication with consent | No (manual) | Google Cloud Console only |
| API Key | Public data, anonymous access | Partial | Console preferred |

For most automation scenarios, **Service Account Keys** are the recommended approach and can be fully scripted. OAuth 2.0 credentials require manual console configuration but the project setup can be automated.

---

## Sources

- [Create and delete service account keys - Google Cloud IAM](https://docs.cloud.google.com/iam/docs/keys-create-delete)
- [Create service accounts - Google Cloud IAM](https://docs.cloud.google.com/iam/docs/service-accounts-create)
- [Enable and disable services - Google Cloud Service Usage](https://docs.cloud.google.com/service-usage/docs/enable-disable)
- [Create access credentials - Google Workspace](https://developers.google.com/workspace/guides/create-credentials)
- [Creating and managing projects - Google Cloud Resource Manager](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)
- [gcloud services enable reference](https://cloud.google.com/sdk/gcloud/reference/services/enable)
