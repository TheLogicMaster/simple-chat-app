#!/bin/bash

# Disable need for user intervention for table outputs
export AWS_PAGER=""

echo "Deleting role..."
aws iam detach-role-policy --role-name simple-chat --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam detach-role-policy --role-name simple-chat --policy-arn arn:aws:iam::aws:policy/AmazonCognitoReadOnly
aws iam delete-role --role-name simple-chat

echo "Deleting lambda functions..."
for f in *.py; do
  name="${f%.py}"
  echo "Deleting Lambda function ${name}..."
  aws lambda delete-function --function-name "${name}" >&-
done

echo "Deleting user pools..."
pools=$(aws cognito-idp list-user-pools --max-results 60 --output json)
for k in $(jq ".UserPools | keys | .[]" <<<"${pools}"); do
  pool=$(jq -r ".UserPools[${k}]" <<<"${pools}")
  name=$(jq -r ".Name" <<<"${pool}")
  id=$(jq -r ".Id" <<<"${pool}")
  if [ "${name}" == "simple-chat-users" ]; then
    echo "Deleting user pool ${id}..."
    aws cognito-idp delete-user-pool --user-pool-id "${id}" >&-
  fi
done

echo "Deleting DynamoDB tables..."
aws dynamodb delete-table --table-name simple-chat-conversations >&-
aws dynamodb delete-table --table-name simple-chat-users >&-

echo "Deleting user APIs..."
apis=$(aws apigatewayv2 get-apis --output json)
for k in $(jq ".Items | keys | .[]" <<<"${apis}"); do
  pool=$(jq -r ".Items[${k}]" <<<"${apis}")
  name=$(jq -r ".Name" <<<"${pool}")
  id=$(jq -r ".ApiId" <<<"${pool}")
  if [ "${name}" == "simple-chat-api" ]; then
    echo "Deleting user API ${id}..."
    aws apigatewayv2 delete-api --api-id "${id}" >&-
  fi
done

echo "Deleted AWS stack!"