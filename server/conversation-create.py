import json
import boto3
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
cognito = boto3.client('cognito-idp')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        # Todo: Verify input

        # Generate unique id
        while True:
            conversation_id = str(uuid.uuid4())
            response = table.get_item(Key={'id': conversation_id})
            if 'Item' not in response:
                break

        table.put_item(Item={
            'id': conversation_id,
            'users': data['users'],
            'name': data['name'],
            'messages': []
        })
        return json.dumps({'id': conversation_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
