# Configuring Terraform itself
terraform {
    # This specifies that we need the "google" provider and which version we want.
    # Pinning versions is a best practice to prevent unexpected breaking changes.
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "~> 5.10"
        }
    }
    # This is the most important block for team collaboration.
    # It tells Terraform to store its state file in a GCS bucket, not on the local
    backend "gcs" {
        bucket = "caramel-banana-2212-0802-tfstate"
        prefix = "terraform/state"
    }
}
# This block configures the Google Cloud provider itself.
provider "google" {
    project = "caramel-banana-2212-0802"
    region = "asia-south1"
    zone = "asia-south1-a"
}