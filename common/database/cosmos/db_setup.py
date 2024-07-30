from azure.cosmos import CosmosClient, PartitionKey

def setup_database(uri, key, database_name, container_name):
    client = CosmosClient(uri, key)
    database = client.create_database_if_not_exists(id=database_name)
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="email"),
        offer_throughput=400
    )
    return client, container