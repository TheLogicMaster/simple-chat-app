import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-users')


def lambda_handler(event, context):
    try:
        table.put_item(Item={
            'username': event['userName'],
            'friends': []
        })
        return event
    except ClientError as e:
        print(e.response['Error']['Message'])
        return
