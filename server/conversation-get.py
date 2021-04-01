import json
import decimal
import boto3
from botocore.exceptions import ClientError

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
    if 'conversation' not in data:
        return {'statusCode': 400}

    conversation_id = data['conversation']

    # Verify client input types
    if type(conversation_id) is not str:
        return {'statusCode': 400}

    try:  # Todo: Filter messages using a 'since' parameter to only get new messages
        response = table.get_item(Key={'id': conversation_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}

    if 'Item' in response:
        return json.dumps(response['Item'], cls=DecimalEncoder) if username in response['Item']['users'] else {'statusCode': 401}
    else:
        return {'statusCode': 404, 'body': 'No such conversation'}
