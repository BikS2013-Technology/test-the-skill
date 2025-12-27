# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Define service account details
export SA_NAME="claude-skills-sa"
export SA_DISPLAY_NAME="Claude Skills Service Account"
export SA_DESCRIPTION="Service account to be used by Claude Skills"

# Create the service account
gcloud iam service-accounts create $SA_NAME \
    --display-name="$SA_DISPLAY_NAME" \
    --description="$SA_DESCRIPTION" \
    --project=$PROJECT_ID