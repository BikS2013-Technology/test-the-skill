#!/bin/bash
# Test Script: validate-api-names.sh
# From document: Google-Cloud-Credentials-Guide.md
# Document lines: 419-443 (Common API Service Names table)
#
# Validates that API service names from the document are recognized by gcloud

echo "=== Validating API Service Names from Document ==="
echo ""

# API names from the document's reference table
APIS=(
    "sheets.googleapis.com"
    "drive.googleapis.com"
    "gmail.googleapis.com"
    "calendar-json.googleapis.com"
    "docs.googleapis.com"
    "vision.googleapis.com"
    "translate.googleapis.com"
    "speech.googleapis.com"
    "texttospeech.googleapis.com"
    "language.googleapis.com"
    "bigquery.googleapis.com"
    "storage.googleapis.com"
    "compute.googleapis.com"
    "cloudfunctions.googleapis.com"
    "run.googleapis.com"
    "container.googleapis.com"
    "sqladmin.googleapis.com"
    "aiplatform.googleapis.com"
    "iam.googleapis.com"
    "oauth2.googleapis.com"
    "people.googleapis.com"
    "iamcredentials.googleapis.com"
)

PASS=0
FAIL=0

echo "Checking API availability (this checks against gcloud services list --available)..."
echo ""

for api in "${APIS[@]}"; do
    echo -n "  $api... "
    # Check if API exists in available services
    if gcloud services list --available --filter="name:$api" --format="value(name)" 2>/dev/null | grep -q "$api"; then
        echo "VALID"
        ((PASS++))
    else
        echo "NOT FOUND"
        ((FAIL++))
    fi
done

echo ""
echo "=== Summary ==="
echo "Valid APIs: $PASS"
echo "Not Found: $FAIL"
