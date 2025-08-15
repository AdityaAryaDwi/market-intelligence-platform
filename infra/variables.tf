variable "project_id" {
    description = "The GCP project ID to deploy resources into."
    type = string
}
variable "region" {
    description = "The primary region for resources."
    type =  string
    default = "asia-south1"
}
variable "confluent_cloud_api_key" {
    description = "The API key for Confluent Cloud."
    type = string
    sensitive = true
}
variable "confluent_cloud_api_secret" {
    description = "The API secret for Confluent Cloud."
    type = string
    sensitive = true
}
variable "kafka_cluster_api_key" {
    description = "API key for a specific Kafka cluster."
    type = string
    sensitive = true
}
variable "kafka_cluster_api_secret" {
    description = "API secret for a specific Kafka cluster."
    type = string
    sensitive = true
}