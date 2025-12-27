#!/bin/bash
# Test Script: create-multi-service-credentials.sh
# From document: Google-Cloud-Credentials-Guide.md
# Document lines: 203-264
#
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
