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
    if 'conversation' not in data or 'user' not in data:
        return {'statusCode': 400}

    conversation_id = data['conversation']
    user = data['user']

    # Verify client input types
    if type(conversation_id) is not str or type(user) is not str:
        return {'statusCode': 400}

    # Make user lowercase
    user = user.lower()

    key = {'id': conversation_id}

    try:
        # Ensure conversation exists
        response = table.get_item(Key=key, AttributesToGet=['users', 'admins'])
        if 'Item' not in response:
            return {'statusCode': 404, 'body': 'No such conversation'}

        admins = response['Item']['admins']
        users = response['Item']['users']

        # Ensure user permissions
        if username not in users:
            return {'statusCode': 401}

        # Ensure target user is a member
        if user not in users:
            return {'statusCode': 404, 'body': 'No such conversation member'}

        # Ensure user isn't already an admin
        if user in admins:
            return {'statusCode': 200, 'body': 'User is already a conversation admin'}

        # Update conversation
        table.update_item(
            Key=key,
            UpdateExpression='set #admins = list_append(#admins, :user)',
            ExpressionAttributeValues={':user': [user]},
            ExpressionAttributeNames={'#admins': 'admins'}
        )
        return 'OK'
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
