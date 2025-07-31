# GCP provider configuration
terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "~> 5.0"
        }
    }
}

provider "google" {
    project = "valiant-hexagon-467515-e8"
    region = "asia-south1"
}