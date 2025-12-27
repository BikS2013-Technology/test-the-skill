# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Define service account details
export SA_NAME="claude-skills-sa"
export SA_DISPLAY_NAME="Claude Skills Service Account"
export SA_DESCRIPTION="Service account to be used by Claude Skills"

# List service accounts to verify
gcloud iam service-accounts list --project=$PROJECT_ID

# Get service account email
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Service Account Email: $SA_EMAIL"