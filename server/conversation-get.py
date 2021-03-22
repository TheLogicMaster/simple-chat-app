import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    data = json.loads(event['body'])
    try:
        response = table.get_item(Key={'id': data['conversation']})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}

    if 'Item' in response:
        return json.dumps(response.get('Item'))
    else:
        return {'statusCode': 404}
