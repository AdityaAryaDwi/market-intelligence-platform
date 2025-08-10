# A resource block defines a piece of infrastructure.
# "google_storage_bucket" is the resource type.
# "bronze_bucket" is our local name for it within Terraform.
resource "google_storage_bucket" "bronze_bucket" {
    name = "${var.project_id}-bronze-data"
    location = var.region
    storage_class = "STANDARD"
    # This section configures the bucket to delete old files automatically after a year.
    # It's good practice for cost management in a bronze layer.
    lifecycle_rule {
        condition {
            age = 365 // days
        }
        action {
            type = "Delete"
        }
    }
    # This enforces that all objects in the bucket are encrypted. A key security feature.
    uniform_bucket_level_access = true
}