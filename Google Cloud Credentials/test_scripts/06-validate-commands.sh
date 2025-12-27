#!/bin/bash
# Test Script: validate-commands.sh
# From document: Google-Cloud-Credentials-Guide.md
# Document lines: 450-605 (Command Reference sections)
#
# Validates gcloud command syntax by checking --help for each command

echo "=== Validating gcloud Commands from Document ==="
echo ""

PASS=0
FAIL=0

validate_command() {
    local cmd="$1"
    local description="$2"

    echo -n "Testing: $description... "

    # Check if command exists by calling --help
    if $cmd --help >/dev/null 2>&1; then
        echo "PASS"
        ((PASS++))
    else
        echo "FAIL (command: $cmd)"
        ((FAIL++))
    fi
}

echo "--- Project Management Commands ---"
validate_command "gcloud projects list" "List projects"
validate_command "gcloud projects create" "Create project"
validate_command "gcloud config set project" "Set current project"
validate_command "gcloud config get-value" "Get config value"

echo ""
echo "--- Billing Commands ---"
validate_command "gcloud beta billing accounts list" "List billing accounts"
validate_command "gcloud beta billing projects link" "Link billing to project"
validate_command "gcloud beta billing projects describe" "Describe project billing"

echo ""
echo "--- Service Account Commands ---"
validate_command "gcloud iam service-accounts list" "List service accounts"
validate_command "gcloud iam service-accounts create" "Create service account"
validate_command "gcloud iam service-accounts delete" "Delete service account"
validate_command "gcloud iam service-accounts keys list" "List SA keys"
validate_command "gcloud iam service-accounts keys create" "Create SA key"
validate_command "gcloud iam service-accounts keys delete" "Delete SA key"

echo ""
echo "--- API/Services Commands ---"
validate_command "gcloud services list" "List services"
validate_command "gcloud services enable" "Enable service"
validate_command "gcloud services disable" "Disable service"

echo ""
echo "--- IAM Commands ---"
validate_command "gcloud projects get-iam-policy" "Get IAM policy"
validate_command "gcloud projects add-iam-policy-binding" "Add IAM binding"
validate_command "gcloud projects remove-iam-policy-binding" "Remove IAM binding"

echo ""
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "All commands validated successfully!"
    exit 0
else
    echo "Some commands failed validation"
    exit 1
fi
