import json
from datetime import datetime
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
    if 'conversation' not in data or 'message' not in data:
        return {'statusCode': 400}

    conversation_id = data['conversation']
    message = data['message']

    # Verify client input types
    if type(conversation_id) is not str or type(message) is not str:
        return {'statusCode': 400}

    key = {'id': conversation_id}

    try:
        response = table.get_item(Key=key, AttributesToGet=['users'])

        # Ensure conversation exists
        if 'Item' not in response:
            return {'statusCode': 404, 'body': 'No such conversation'}

        # Ensure user is in conversation
        if username not in response['Item']['users']:
            return {'statusCode': 401}

        # Update conversation
        table.update_item(
            Key=key,
            UpdateExpression='set #messages = list_append(#messages, :message)',
            ExpressionAttributeValues={':message': [{
                'type': 'text',
                'user': username,
                'timestamp': int(datetime.now().timestamp()),
                'content': message
            }]},
            ExpressionAttributeNames={'#messages': 'messages'}
        )
        return 'OK'
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
