variable "project_id" {
    description = "The GCP project ID to deploy resources into."
    type = string
}
variable "region" {
    description = "The primary region for resources."
    type =  string
    default = "asia-south1
}