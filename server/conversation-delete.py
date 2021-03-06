import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    # Ensure message has a body
    if 'body' not in event:
        return {'statusCode': 400}

    data = json.loads(event['body'])
    username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']

    # Verify client input
    if 'conversation' not in data:
        return {'statusCode': 400}

    conversation_id = data['conversation']

    # Verify client input types
    if type(conversation_id) is not str:
        return {'statusCode': 400}

    key = {'id': conversation_id}

    try:
        # Ensure conversation exists
        response = table.get_item(Key=key)
        if 'Item' not in response:
            return {'statusCode': 404, 'body': 'No such conversation'}

        # Ensure user is admin
        if username not in response['Item']['admins']:
            return {'statusCode': 401}

        # Delete conversation
        table.delete_item(Key=key)
        return 'OK'
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
