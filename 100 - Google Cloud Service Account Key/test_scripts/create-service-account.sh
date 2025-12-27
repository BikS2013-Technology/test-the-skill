#!/bin/bash
# create-service-account.sh
# Creates a service account and key for Python scripting
# FROM DOCUMENT: Lines 290-380

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
