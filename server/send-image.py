import boto3
from botocore.exceptions import ClientError
import uuid
import json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    data = json.loads(event['body'])
    username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']

    # Verify client input
    if 'conversation' not in data:
        return {'statusCode': 400}

    conversation_id = data['conversation']

    # Verify client input types
    if type(conversation_id) is not str:
        return {'statusCode': 400}

    try:
        response = table.get_item(Key={'id': conversation_id}, AttributesToGet=['users'])

        # Ensure conversation exists
        if 'Item' not in response:
            return {'statusCode': 404, 'body': 'No such conversation'}

        # Ensure user is in conversation
        if username not in response['Item']['users']:
            return {'statusCode': 401}

        # Find S3 Bucket
        response = s3.list_buckets()
        buckets = response['Buckets']
        bucket = None
        for entry in buckets:
            if entry['Name'].startswith('simple-app-bucket-'):
                # Detect "Ghost" Buckets
                try:
                    s3.head_bucket(Bucket=entry['Name'])
                    bucket = entry['Name']
                    break
                except ClientError:
                    print('Found ghost bucket? Bucket: ' + entry['Name'])

        # Ensure bucket exists
        if bucket is None:
            print('Failed to get Bucket')
            return {'statusCode': 500}

        # Return pre-signed upload URL data
        return s3.generate_presigned_post(
            Bucket=bucket,
            Key='conversations/' + str(uuid.uuid4()),
            Fields={
                'x-amz-meta-username': username,
                'x-amz-meta-conversation': conversation_id,
                'acl': 'public-read'
            },
            Conditions=[
                ['content-length-range', 10, 3000000],
                {'x-amz-meta-username': username},
                {'x-amz-meta-conversation': conversation_id},
                {'acl': 'public-read'}
            ]
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
