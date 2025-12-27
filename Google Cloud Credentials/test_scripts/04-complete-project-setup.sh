#!/bin/bash
# Test Script: complete-project-setup.sh
# From document: Google-Cloud-Credentials-Guide.md
# Document lines: 272-351
#
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
