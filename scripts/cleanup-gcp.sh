set -euo pipefail

        PROJECT="dcisionai"
        echo "▶ Cleaning up project: $PROJECT"
        gcloud config set project "$PROJECT"

        # 1) DELETE Compute Engine resources
        echo "  • Deleting Compute Engine VMs…"
        gcloud compute instances list --format="value(name,zone)" \
          | while read -r NAME ZONE; do
              gcloud compute instances delete "$NAME" --zone="$ZONE" --quiet
            done

        echo "  • Deleting disks…"
        gcloud compute disks list --format="value(name,zone)" \
          | while read -r NAME ZONE; do
              gcloud compute disks delete "$NAME" --zone="$ZONE" --quiet
            done

        echo "  • Deleting snapshots…"
        gcloud compute snapshots list --format="value(name)" \
          | while read -r NAME; do
              gcloud compute snapshots delete "$NAME" --quiet
            done

        echo "  • Deleting custom images…"
        gcloud compute images list --filter="family:* OR deprecated.state=* " --format="value(name)" \
          | while read -r NAME; do
              gcloud compute images delete "$NAME" --quiet
            done

        echo "  • Deleting firewall rules…"
        gcloud compute firewall-rules list --format="value(name)" \
          | while read -r NAME; do
              gcloud compute firewall-rules delete "$NAME" --quiet
            done

        echo "  • Deleting networks (incl. default)…"
        gcloud compute networks list --format="value(name)" \
          | while read -r NAME; do
              gcloud compute networks delete "$NAME" --quiet
            done

        # 2) Kubernetes / GKE
        echo "  • Deleting GKE clusters…"
        gcloud container clusters list --format="value(name,location)" \
          | while read -r NAME LOCATION; do
              gcloud container clusters delete "$NAME" --zone="$LOCATION" --quiet
            done

        # 3) Cloud SQL
        echo "  • Deleting Cloud SQL instances…"
        gcloud sql instances list --format="value(name)" \
          | while read -r NAME; do
              gcloud sql instances delete "$NAME" --quiet
            done

        # 4) Pub/Sub
        echo "  • Deleting Pub/Sub subscriptions…"
        gcloud pubsub subscriptions list --format="value(name)" \
          | while read -r NAME; do
              gcloud pubsub subscriptions delete "$NAME" --quiet
            done

        echo "  • Deleting Pub/Sub topics…"
        gcloud pubsub topics list --format="value(name)" \
          | while read -r NAME; do
              gcloud pubsub topics delete "$NAME" --quiet
            done

        # 5) Cloud Storage
        echo "  • Deleting GCS buckets…"
        gsutil ls -p "$PROJECT" \
          | while read -r BUCKET; do
              gsutil rm -r "$BUCKET"
            done

        # 6) BigQuery
        echo "  • Deleting BigQuery datasets…"
        bq --project_id="$PROJECT" ls --format=prettyjson \
          | jq -r '.[].datasetReference.datasetId' \
          | while read -r DS; do
              bq rm -r -f -d "$PROJECT:$DS"
            done

        # 7) Cloud Functions
        echo "  • Deleting Cloud Functions…"
        gcloud functions list --format="value(name,region)" \
          | while read -r NAME REGION; do
              gcloud functions delete "$NAME" --region="$REGION" --quiet
            done

        # 8) Cloud Run (fully-managed)
        echo "  • Deleting Cloud Run services…"
        gcloud run services list --platform=managed --format="value(name,location)" \
          | while read -r NAME LOCATION; do
              gcloud run services delete "$NAME" --region="$LOCATION" --platform=managed --quiet
            done

        # 9) Dataflow
        echo "  • Cancelling Dataflow jobs…"
        for R in $(gcloud dataflow jobs list --format="value(region)" --regions="$(gcloud dataflow locations list --format='value(location)')"); do
          gcloud dataflow jobs list --format="value(id)" --region="$R" \
            | while read -r JID; do
                gcloud dataflow jobs cancel "$JID" --region="$R"
              done
        done

        # 10) Composer
        echo "  • Deleting Composer environments…"
        gcloud composer environments list --locations="-" --format="value(name,location)" \
          | while read -r NAME LOCATION; do
              gcloud composer environments delete "$NAME" --location="$LOCATION" --quiet
            done

        # 11) Artifact Registry (and Docker Registry)
        echo "  • Deleting Artifact Registry repos…"
        gcloud artifacts repositories list --format="value(name,location)" \
          | while read -r NAME LOCATION; do
              gcloud artifacts repositories delete "$NAME" --location="$LOCATION" --quiet
            done

        # 12) Cloud Build triggers
        echo "  • Deleting Cloud Build triggers…"
        gcloud beta builds triggers list --format="value(id)" \
          | while read -r TR; do
              gcloud beta builds triggers delete "$TR" --quiet
            done

        # 13) Deployment Manager
        echo "  • Deleting Deployment Manager deployments…"
        gcloud deployment-manager deployments list --format="value(name)" \
          | while read -r D; do
              gcloud deployment-manager deployments delete "$D" --quiet
            done

        # 14) Finally disable all enabled GCP APIs (except serviceusage)
        echo "  • Disabling all enabled services…"
        gcloud services list --enabled --format="value(config.name)" \
          | grep -v serviceusage.googleapis.com \
          | xargs -r -n1 gcloud services disable --quiet

        echo "✅ Cleanup complete. All user-managed resources in project '${PROJECT}' have been deleted."

