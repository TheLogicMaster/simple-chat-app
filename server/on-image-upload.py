import boto3
from botocore.exceptions import ClientError
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    image = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']
    metadata = s3.get_object(
        Bucket=bucket,
        Key=image
    )['Metadata']

    # Ensure this is a conversation image
    if image.startswith('conversations/'):
        conversation_id = metadata['conversation']
        username = metadata['username']
        key = {'id': conversation_id}
        try:
            response = table.get_item(Key=key, AttributesToGet=['users'])

            # Ensure conversation exists
            if 'Item' not in response:
                print('Conversation not found')
                return

            # Ensure user is in conversation
            if username not in response['Item']['users']:
                print('User not in conversation')
                return

                # Update conversation
            table.update_item(
                Key=key,
                UpdateExpression='set #messages = list_append(#messages, :message)',
                ExpressionAttributeValues={':message': [{
                    'type': 'image',
                    'user': username,
                    'timestamp': int(datetime.now().timestamp()),
                    'content': f'https://{bucket}.s3.amazonaws.com/{image}'
                }]},
                ExpressionAttributeNames={'#messages': 'messages'}
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return

    return event
