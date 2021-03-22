import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    data = json.loads(event['body'])
    try:
        key = {'id': data['conversation']}

        # Ensure conversation exists
        response = table.get_item(Key=key)
        if 'Item' not in response:
            return {'statusCode': 404}

        # Ensure user is part of conversation
        username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']
        if username not in response['Item']['users']:
            return {'statusCode': 401}

        table.delete_item(Key=key)
        return 'OK'
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
