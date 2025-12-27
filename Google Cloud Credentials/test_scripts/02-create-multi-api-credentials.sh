#!/bin/bash
# Test Script: create-multi-api-credentials.sh
# From document: Google-Cloud-Credentials-Guide.md
# Document lines: 134-199
#
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
