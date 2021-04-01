import json
import decimal
import boto3
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-conversations')


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def lambda_handler(event, context):
    # Ensure message has a body
    if 'body' not in event:
        return {'statusCode': 400}

    data = json.loads(event['body'])
    username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']

    # Verify client input
    if 'friend' not in data:
        return {'statusCode': 400}

    friend = data['friend']

    # Verify client input types
    if type(friend) is not str:
        return {'statusCode': 400}

    try:
        # Check for existing conversation
        response = table.scan(
            ProjectionExpression="#id",
            ExpressionAttributeNames={"#id": "id"},
            FilterExpression=Attr('users').contains(username) & Attr('users').contains(friend) & Attr('dm').eq(True)
        )

        if len(response['Items']) == 0:
            # Create conversation if it doesn't exist
            conversation_id = str(uuid.uuid4())
            users = [username, friend]
            table.put_item(Item={
                'id': conversation_id,
                'admins': users,
                'users': users,
                'name': f'{username} and {friend} Direct Messages',
                'dm': True,
                'messages': []
            })
            return {'id': conversation_id}
        else:
            return {'id': response["Items"][0]["id"]}
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
