#!/bin/bash
set -e

LOCATION=us-west1
GCLOUD_PROJECT=stampy-nlp
CLOUD_RUN_SERVICE=stampy-chat
IMAGE=$LOCATION-docker.pkg.dev/$GCLOUD_PROJECT/cloud-run-source-deploy/$CLOUD_RUN_SERVICE

# echo "Running tests:"
# pytest --runlive

echo
echo "Will execute the following actions:"
echo "--> Build a docker image"
echo "--> Push the image as $IMAGE"
echo "--> Deploy the image as the $CLOUD_RUN_SERVICE service"
read -r -p "Is that correct? [y/N] " response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    exit 1
fi

echo
echo "Enabling Google API"
gcloud config set project $GCLOUD_PROJECT
gcloud config set run/region $LOCATION
gcloud services enable iam.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable logging.googleapis.com
gcloud auth configure-docker us-west1-docker.pkg.dev

echo "Building image"

docker pull --platform linux/amd64 python:3.8
docker buildx build --platform linux/amd6 -t $IMAGE .
docker push $IMAGE\:latest

echo "Deploying to Google Cloud Run"

gcloud beta run deploy $CLOUD_RUN_SERVICE --image $IMAGE\:latest \
--platform managed --no-traffic --tag=test \
--service-account=service@stampy-nlp.iam.gserviceaccount.com

echo
echo "Project ID: $GCLOUD_PROJECT"
