#!/bin/bash

# Configuration
PREFIX="julien-prefix"
STAGING_PROJECT="immersion-day-staging-008"
PROD_PROJECT="immersion-day-prod-008"

# Path to the terraform directory relative to where the script is run
TF_DIR="deployment/terraform"

echo "=== Starting Comprehensive Cleanup for Prefix: $PREFIX ==="

# 0. Delete local Terraform state caches
echo "Cleaning up local Terraform state caches..."
if [ -d "$TF_DIR/.terraform" ]; then
    echo "Deleting $TF_DIR/.terraform"
    rm -rf "$TF_DIR/.terraform"
fi
if [ -f "$TF_DIR/.terraform.lock.hcl" ]; then
    echo "Deleting $TF_DIR/.terraform.lock.hcl"
    rm -f "$TF_DIR/.terraform.lock.hcl"
fi

delete_resources_for_project() {
    local PROJECT=$1
    echo "--- Processing Project: $PROJECT ---"

    # 1. Delete Service Accounts
    echo "Searching for Service Accounts..."
    SAs=$(gcloud iam service-accounts list --project="$PROJECT" --filter="email ~ ^$PREFIX" --format="value(email)" --quiet 2>/dev/null)
    for SA in $SAs; do
        echo "Deleting Service Account: $SA"
        gcloud iam service-accounts delete "$SA" --project="$PROJECT" --quiet
    done

    # 2. Delete GCS Buckets
    echo "Searching for GCS Buckets..."
    Buckets=$(gcloud storage buckets list --project="$PROJECT" --filter="name ~ ^$PROJECT-$PREFIX" --format="value(name)" --quiet 2>/dev/null)
    Buckets2=$(gcloud storage buckets list --project="$PROJECT" --filter="name ~ $PREFIX" --format="value(name)" --quiet 2>/dev/null)
    CombinedBuckets=$(echo -e "$Buckets\n$Buckets2" | sort -u)
    for b in $CombinedBuckets; do
        if [ -n "$b" ]; then
            echo "Deleting Bucket: $b"
            gcloud storage buckets delete "gs://$b" --project="$PROJECT" --quiet
        fi
    done

    # 3. Delete BigQuery Datasets
    echo "Searching for BigQuery Datasets..."
    Datasets=$(bq ls --project_id="$PROJECT" | grep -E "^\\s*$PREFIX" | awk '{print $1}')
    for ds in $Datasets; do
        echo "Deleting BigQuery Dataset: $ds"
        bq rm -f -r -d "$PROJECT:$ds"
    done

    # 4. Delete BigQuery Connections
    echo "Searching for BigQuery Connections..."
    Connections=$(bq ls --connection --project_id="$PROJECT" | grep "$PREFIX" | awk '{print $1}')
    for conn in $Connections; do
        echo "Deleting BigQuery Connection: $conn"
        bq rm -f -c "$PROJECT:locations/europe-west1/connections/$conn"
    done
    
    # 5. Delete Cloud Build Triggers
    echo "Searching for Cloud Build Triggers..."
    # Added --quiet here to prevent it from hanging on prompts if the API is not enabled
    Triggers=$(gcloud builds triggers list --project="$PROJECT" --region=europe-west1 --format="value(name)" --filter="name ~ $PREFIX" --quiet 2>/dev/null)
    for t in $Triggers; do
        echo "Deleting Trigger: $t"
        gcloud builds triggers delete "$t" --project="$PROJECT" --region=europe-west1 --quiet
    done
}

delete_resources_for_project "$STAGING_PROJECT"
delete_resources_for_project "$PROD_PROJECT"

echo "=== Cleanup Complete ==="
