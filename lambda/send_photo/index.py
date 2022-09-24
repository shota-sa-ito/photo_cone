import boto3
import os


def lambda_handler(event, context):
    post_data = json.loads(event.get('body', '{}')).get('data')
    print(post_data)
    domain_name = event.get('requestContext', {}).get('domainName')
    stage = event.get('requestContext', {}).get('stage')

    dynamo_client = boto3.client('dynamodb')

    dynamo_resp = dynamo_client.scan(
        TableName=os.environ['table'],
    )
    items = dynamo_resp.get('Items')
    if items is None:
        return {'statusCode': 500, 'body': 'something went wrong'}

    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")
    for item in items:
        try:
            print(item)
            _ = apigw_management.post_to_connection(ConnectionId=item['id'], Data=post_data)
        except:
            pass

    return {'statusCode': 200, 'body': 'ok'}
