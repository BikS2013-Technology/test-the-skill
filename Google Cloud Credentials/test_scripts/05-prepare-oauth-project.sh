#!/bin/bash
# Test Script: prepare-oauth-project.sh
# From document: Google-Cloud-Credentials-Guide.md
# Document lines: 382-415
#
# Prepares a project for OAuth credentials (manual OAuth setup still required)

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
