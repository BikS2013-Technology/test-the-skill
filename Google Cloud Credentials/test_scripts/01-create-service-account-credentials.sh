#!/bin/bash
# Test Script: create-service-account-credentials.sh
# From document: Google-Cloud-Credentials-Guide.md
# Document lines: 69-130
#
# Creates a service account with credentials.json for a single API

set -e  # Exit on error

# Configuration - MODIFY THESE VALUES
PROJECT_ID="my-project-id"
SERVICE_ACCOUNT_NAME="my-service-account"
DISPLAY_NAME="My Service Account"
DESCRIPTION="Service account for API access"
KEY_FILE="./credentials.json"
API_TO_ENABLE="sheets.googleapis.com"  # Example: Google Sheets API
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
