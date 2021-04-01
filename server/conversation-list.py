import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('simple-chat-conversations')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['jwt']['claims']['cognito:username']

    try:
        response = table.scan(
            ProjectionExpression="#id, #name, #users, admins, dm",
            FilterExpression=Attr('users').contains(username),
            ExpressionAttributeNames={'#id': 'id', '#name': 'name', '#users': 'users'}
        )
        return response['Items']
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500}
