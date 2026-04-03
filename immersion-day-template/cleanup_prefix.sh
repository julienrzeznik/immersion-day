#!/bin/bash

# Configuration
PREFIX="julien-agent"
STAGING_PROJECT="immersion-day-staging-009"
PROD_PROJECT="immersion-day-prod-009"
REGION="europe-west1"

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
    # Replace hyphens with underscores for BQ dataset search
    BQ_PREFIX=$(echo "$PREFIX" | tr '-' '_')
    Datasets=$(bq ls --project_id="$PROJECT" | grep -E "^\\s*$BQ_PREFIX" | awk '{print $1}')
    for ds in $Datasets; do
        echo "Deleting BigQuery Dataset: $ds"
        bq rm -f -r -d "$PROJECT:$ds"
    done

    # 4. Delete BigQuery Connections
    echo "Searching for BigQuery Connections..."
    Connections=$(bq ls --connection --project_id="$PROJECT" --location=$REGION | grep "$PREFIX" | awk '{print $1}')
    for conn in $Connections; do
        echo "Deleting BigQuery Connection: $conn"
        bq rm -f --connection "$conn"
    done
    
    # 5. Delete Cloud Build Triggers
    echo "Searching for Cloud Build Triggers..."
    # Added --quiet here to prevent it from hanging on prompts if the API is not enabled
    Triggers=$(gcloud builds triggers list --project="$PROJECT" --region=$REGION --format="value(name)" --filter="name ~ $PREFIX" --quiet 2>/dev/null)
    for t in $Triggers; do
        echo "Deleting Trigger: $t"
        gcloud builds triggers delete "$t" --project="$PROJECT" --region=$REGION --quiet
    done

    # 6. Delete Logging Linked Datasets
    echo "Searching for Logging Linked Datasets..."
    # The link ID usually follows the pattern prefix_genai_telemetry_logs
    LINK_ID="${PREFIX//-/_}_genai_telemetry_logs"
    BUCKET_ID="${PREFIX}-genai-telemetry"
    
    echo "Attempting to delete Logging Link: $LINK_ID in bucket $BUCKET_ID"
    gcloud logging links delete "$LINK_ID" --bucket="$BUCKET_ID" --location=$REGION --project="$PROJECT" --quiet 2>/dev/null || echo "Link not found or already deleted."
}

delete_resources_for_project "$STAGING_PROJECT"
delete_resources_for_project "$PROD_PROJECT"

echo "=== Cleanup Complete ==="
