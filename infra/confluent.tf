# Creating a new environment in Confluent Cloud to hold our resources.
resource "confluent_environment" "development" {
    display_name = "Development"
}
# Creating a new "BASIC" Kafka cluster within our new environment.
resource "confluent_kafka_cluster" "basic_cluster" {
    display_name = "market-intel-cluster"
    availability = "SINGLE_ZONE"
    cloud = "GCP"
    region = var.region
    environment {
        id = confluent_environment.development.id
    }
    basic{} # An empty block specifies a BASIC cluster type.
    # We add a lifecycle block to prevent accidental deletion.
    # This is a good safety measure for stateful resources like a Kafka cluster.
    lifecycle {
        prevent_destroy = true
    }
}
# Creating a Kafka topic for our raw stock data
resource "confluent_kafka_topic" "raw_ticks" {
    topic_name = "raw_stock_ticks"
    partitions_count = 3
    kafka_cluster {
        id = confluent_kafka_cluster.basic_cluster.id
    }
    rest_endpoint = confluent_kafka_cluster.basic_cluster.rest_endpoint
    credentials {
        key = var.kafka_cluster_api_key
        secret = var.kafka_cluster_api_secret
    }
}
# Output the bootstrap server URL so we can use it in our client applications
output "kafka_bootstrap_server" {
    description = "The bootstrap server URL for the Kafka cluster."
    value = confluent_kafka_cluster.basic_cluster.bootstrap_endpoint
    sensitive = false
}