# The role must be passed as parameter to the script 
# indicative roles: storage.admin, bigquery.user, pubsub.publisher
# look at the end of the script for examples

# Check if argument was provided
if [ -z "$1" ]; then
    echo "Error: Role name required"
    echo "Usage: $0 <role>"
    echo "Examples: storage.admin, bigquery.user, pubsub.publisher"
    exit 1
fi

# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Define service account details
export SA_NAME="claude-skills-sa"
export SA_DISPLAY_NAME="Claude Skills Service Account"
export SA_DESCRIPTION="Service account to be used by Claude Skills"

export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/${1}"



# # Storage Admin (for Cloud Storage access)
# gcloud projects add-iam-policy-binding $PROJECT_ID \
#     --member="serviceAccount:$SA_EMAIL" \
#     --role="roles/storage.admin"

# # BigQuery User (for BigQuery access)
# gcloud projects add-iam-policy-binding $PROJECT_ID \
#     --member="serviceAccount:$SA_EMAIL" \
#     --role="roles/bigquery.user"

# # Pub/Sub Publisher (for Pub/Sub access)
# gcloud projects add-iam-policy-binding $PROJECT_ID \
#     --member="serviceAccount:$SA_EMAIL" \
#     --role="roles/pubsub.publisher"