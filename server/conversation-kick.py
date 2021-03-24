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

    key = {'id': conversation_id}

    try:
        response = table.get_item(
            Key=key,
            ProjectionExpression='#users, admins',
            ExpressionAttributeNames={'#users': 'users'}
        )

        # Ensure conversation exists
        if 'Item' not in response:
            return {'statusCode': 404, 'body': 'No such conversation'}

        admins = response['Item']['admins']
        users = response['Item']['users']

        # Ensure target is a conversation member
        if user not in users:
            return {'statusCode': 404, 'body': 'User isn\'t a conversation member'}

        # Ensure user is admin and target isn't admin in conversation
        if username not in admins or user in admins:
            return {'statusCode': 401}

        # Ensure target user isn't the only admin
        if user in admins and len(admins) == 1:
            return {'statusCode': 404, 'body': 'Can\'t remove the only admin from a conversation'}

        users.remove(user)
        if user in admins:
            admins.remove(user)

        # Update conversation
        table.update_item(
            Key=key,
            UpdateExpression="set #users=:users, admins=:admins",
            ExpressionAttributeValues={
                ":users": users,
                ":admins": admins
            },
            ExpressionAttributeNames={'#users': 'users'}
        )
        return 'OK'
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
