# Check if argument was provided
if [ -z "$1" ]; then
    echo "Error: You must provide the folder where the key file will be stored."
    echo "Usage: $0 <folder>"
    echo "Examples: .,  ~/.gcloud"
    exit 1
fi


# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Define service account details
export SA_NAME="claude-skills-sa"
export SA_DISPLAY_NAME="Claude Skills Service Account"
export SA_DESCRIPTION="Service account to be used by Claude Skills"

export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Define key file location
export KEY_FILE="${1}/${SA_NAME}-key.json"

# Create directory if it doesn't exist
mkdir -p $(dirname $KEY_FILE)

# Create the service account key
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

echo "Key created at: $KEY_FILE"