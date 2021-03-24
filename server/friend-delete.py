import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-users')


def lambda_handler(event, context):
    # Ensure message has a body
    if 'body' not in event:
        return {'statusCode': 400}

    data = json.loads(event['body'])
    username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']

    # Verify client input
    if 'user' not in data:
        return {'statusCode': 400}

    user = data['user']

    # Verify client input types
    if type(user) is not str:
        return {'statusCode': 400}

    key = {'username': username}

    try:
        # Get user data
        response = table.get_item(Key=key)

        # Ensure user table entry is present
        if 'Item' not in response:
            print('Failed to get user data for: ' + username)
            return {'statusCode': 500, 'body': 'Missing user data'}

        friends = response['Item']['friends']

        # Ensure user is a friend
        if user not in friends:
            return {'statusCode': 404, 'body': 'No such friend exists to remove'}

        friends.remove(user)

        # Update friends
        table.update_item(
            Key=key,
            UpdateExpression='set #friends = :friends',
            ExpressionAttributeValues={':friends': friends},
            ExpressionAttributeNames={'#friends': 'friends'}
        )
        return 'OK'
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
