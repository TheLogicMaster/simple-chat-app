import json
import boto3
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
cognito = boto3.client('cognito-idp')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    # Ensure message has a body
    if 'body' not in event:
        return {'statusCode': 400}

    data = json.loads(event['body'])
    username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']

    # Verify client input
    if 'name' not in data or type(data['name']) is not str or 'users' not in data or \
            type(data['users']) is not list:
        return {'statusCode': 400}

    name = data['name']
    users = data['users']

    # Verify client input types
    if type(name) is not str or type(users) is not list:
        return {'statusCode': 400}
    for user in users:
        if type(user) is not str:
            return {'statusCode': 400}

    try:
        # Generate unique id
        while True:
            conversation_id = str(uuid.uuid4())
            response = table.get_item(Key={'id': conversation_id})
            if 'Item' not in response:
                break

        # Ensure user is in conversation
        if username not in users:
            users.append(username)

        # Create conversation
        table.put_item(Item={
            'id': conversation_id,
            'admins': [username],
            'users': users,
            'name': name,
            'messages': []
        })
        return json.dumps({'id': conversation_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
