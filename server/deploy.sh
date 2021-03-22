#!/bin/bash

# Disable need for user intervention for table outputs
export AWS_PAGER=""

echo "Creating role..."
role=$(aws iam create-role --role-name simple-chat --no-paginate --assume-role-policy-document \
  '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}' \
  --query 'Role.Arn' --output text) || exit
echo "Created role: ${role}"

echo "Adding role permissions..."
aws iam attach-role-policy --role-name simple-chat --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess || exit
aws iam attach-role-policy --role-name simple-chat --policy-arn arn:aws:iam::aws:policy/AmazonCognitoReadOnly || exit

echo "Waiting for role propagation..."
sleep 10

echo "Creating Lambda functions..."
for f in *.py; do
  name=${f%.py}
  zip -jq "${name}.zip" "${f}" || exit
  echo "Creating function ${name}..."
  aws lambda create-function --function-name "${name}" \
    --zip-file "fileb://${name}.zip" --handler "${name}.lambda_handler" --runtime python3.8 \
    --role "${role}" >&- || exit
  aws lambda add-permission --function-name "${name}" --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com --statement-id api >&- || exit
  rm "${name}.zip"
done

echo "Fetching user ID..."
id=$(aws sts get-caller-identity --query 'Account' --output text) || exit
echo "User ID is ${id}"

echo "Creating Cognito user pool..."
pool=$(aws cognito-idp create-user-pool --pool-name simple-chat-users \
  --username-configuration=CaseSensitive=false --policies=PasswordPolicy='{MinimumLength=8,RequireUppercase=false,RequireLowercase=false,RequireNumbers=false,RequireSymbols=false}' \
  --alias-attributes "preferred_username" "email" "phone_number" \
  --query 'UserPool.Id' --output text) || exit
echo "Created user pool: ${pool}"

echo "Creating user pool client..."
client=$(aws cognito-idp create-user-pool-client --user-pool-id "${pool}" --client-name simple-chat-auth \
  --no-generate-secret --query 'UserPoolClient.ClientId' --output text) || exit
echo "Created client: ${client}"

echo "Creating DynamoDB tables..."
echo "Creating conversations table..."
aws dynamodb create-table \
  --table-name simple-chat-conversations \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 >&- || exit
echo "Creating users table..."
aws dynamodb create-table \
  --table-name simple-chat-users \
  --attribute-definitions AttributeName=username,AttributeType=S \
  --key-schema AttributeName=username,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 >&- || exit
echo "Successfully created tables"

echo "Populating API template IDs..."
cp api-template.yaml api.yaml || exit
sed -i "s/{ID}/${id}/g" api.yaml || exit
sed -i "s/{POOL}/${pool}/g" api.yaml || exit
sed -i "s/{CLIENT}/${client}/g" api.yaml || exit

echo "Creating Gateway API..."
api=$(aws apigatewayv2 import-api --body 'file://api.yaml' --query '[ApiId,ApiEndpoint]' --output json) || exit
rm ./api.yaml
apiId=$(jq -r ".[0]" <<<"${api}")
apiEndpoint=$(jq -r ".[1]" <<<"${api}")
echo "Creating API Stage..."
aws apigatewayv2 create-stage --api-id "${apiId}" --stage-name "\$default" --auto-deploy >&- || exit
echo "Created API with endpoint: ${apiEndpoint}"

echo "Successfully created app AWS stack!"
