import aioboto3

dynamo_client = aioboto3.client("dynamodb", region_name="eu-west-2")

table = dynamo_client.Table("Foo")

