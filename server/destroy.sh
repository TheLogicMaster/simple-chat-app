#!/bin/bash

# Disable need for user intervention for table outputs
export AWS_PAGER=""

echo "Deleting role..."
for permission in AmazonDynamoDBFullAccess AmazonCognitoReadOnly AWSXRayDaemonWriteAccess \
  service-role/AWSLambdaBasicExecutionRole CloudWatchLambdaInsightsExecutionRolePolicy; do
  aws iam detach-role-policy \
    --role-name simple-chat \
    --policy-arn "arn:aws:iam::aws:policy/${permission}" >&-
done
aws iam delete-role \
  --role-name simple-chat

echo "Deleting lambda functions..."
for f in *.py; do
  name="${f%.py}"
  echo "Deleting Lambda function ${name}..."
  aws lambda delete-function \
    --function-name "${name}" >&-
done

# Todo: Create generic function for finding IDs
echo "Deleting user pool..."
pools=$(aws cognito-idp list-user-pools \
  --max-results 60 \
  --output json) || exit
for k in $(jq ".UserPools | keys | .[]" <<<"${pools}"); do
  pool=$(jq -r ".UserPools[${k}]" <<<"${pools}")
  name=$(jq -r ".Name" <<<"${pool}")
  id=$(jq -r ".Id" <<<"${pool}")
  if [ "${name}" == "simple-chat-users" ]; then
    echo "Deleting user pool ${id}..."
    aws cognito-idp delete-user-pool \
      --user-pool-id "${id}" >&-
  fi
done

echo "Deleting DynamoDB tables..."
aws dynamodb delete-table \
  --table-name simple-chat-conversations >&-
aws dynamodb delete-table \
  --table-name simple-chat-users >&-

echo "Deleting user API..."
apis=$(aws apigatewayv2 get-apis \
  --output json) || exit
for k in $(jq ".Items | keys | .[]" <<<"${apis}"); do
  pool=$(jq -r ".Items[${k}]" <<<"${apis}")
  name=$(jq -r ".Name" <<<"${pool}")
  id=$(jq -r ".ApiId" <<<"${pool}")
  if [ "${name}" == "simple-chat-api" ]; then
    echo "Deleting user API ${id}..."
    aws apigatewayv2 delete-api \
      --api-id "${id}" >&-
  fi
done

echo "Deleting Amplify app..."
apis=$(aws amplify list-apps \
  --output json) || exit
for k in $(jq ".apps | keys | .[]" <<<"${apis}"); do
  pool=$(jq -r ".apps[${k}]" <<<"${apis}")
  name=$(jq -r ".name" <<<"${pool}")
  id=$(jq -r ".appId" <<<"${pool}")
  if [ "${name}" == "simple-chat-app" ]; then
    echo "Deleting AWS app: ${id}..."
    aws amplify delete-app \
      --app-id "${id}" >&-
  fi
done

echo "Deleted AWS stack!"
