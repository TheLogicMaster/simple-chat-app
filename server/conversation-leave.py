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
        response = table.get_item(Key=key, AttributesToGet=['users', 'admins'])

        if 'Item' not in response:
            return {'statusCode': 404, 'body': 'No such conversation'}

        admins = response['Item']['admins']
        users = response['Item']['users']

        # Ensure user is in conversation
        if username not in users:
            return {'statusCode': 401}

        # Ensure user isn't the only admin
        if username in admins and len(admins) == 1:
            return {'statusCode': 200, 'body': 'Can\'t remove the only admin from a conversation'}

        admins.remove(username)
        users.remove(username)

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
