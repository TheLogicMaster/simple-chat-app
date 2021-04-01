import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-users')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']

    try:
        # Get user data
        response = table.get_item(Key={'username': username})

        # Ensure user data exists
        if 'Item' not in response:
            print('Failed to get user data for: ' + username)
            return {'statusCode': 500, 'body': 'Missing user data'}

        return response['Item']['friends']
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
