#!/bin/bash

# Disable need for user intervention for table outputs
export AWS_PAGER=""

echo "Creating role..."
role=$(aws iam create-role \
  --role-name simple-chat \
  --no-paginate \
  --assume-role-policy-document \
  '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}' \
  --query 'Role.Arn' \
  --output text) || exit
echo "Created role: ${role}"

echo "Adding role permissions..."
for permission in AmazonDynamoDBFullAccess AmazonCognitoReadOnly AWSXRayDaemonWriteAccess \
  service-role/AWSLambdaBasicExecutionRole CloudWatchLambdaInsightsExecutionRolePolicy AmazonS3FullAccess; do
  aws iam attach-role-policy \
    --role-name simple-chat \
    --policy-arn "arn:aws:iam::aws:policy/${permission}" || exit
done

echo "Waiting for role propagation..."
sleep 10

echo "Creating Lambda functions..."
for f in *.py; do
  name=${f%.py}
  zip -q "${name}.zip" "${f}" || exit
  echo "Creating function ${name}..."
  aws lambda create-function \
    --function-name "${name}" \
    --zip-file "fileb://${name}.zip" \
    --handler "${name}.lambda_handler" \
    --runtime python3.8 \
    --role "${role}" >&- || exit
  if [[ $name == on-user-confirmed ]]; then
    service="cognito-idp"
  elif [[ $name == on-image-upload ]]; then
    service="s3"
  else
    service="apigateway"
  fi
  aws lambda add-permission \
    --function-name "${name}" \
    --action lambda:InvokeFunction \
    --principal "${service}.amazonaws.com" \
    --statement-id api >&- || exit
  rm "${name}.zip"
done

echo "Fetching user ID..."
id=$(aws sts get-caller-identity \
  --query 'Account' \
  --output text) || exit
echo "User ID is ${id}"

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

echo "Creating S3 Bucket..."
bucket=$(aws s3api create-bucket \
  --bucket simple-app-bucket-$((1 + RANDOM % 100000000)) \
  --query "Location" \
  --output text) || exit
bucket="${bucket:1}"
echo "Created Bucket: ${bucket}"

echo "Configuring Bucket..."
aws s3api put-bucket-cors \
  --bucket "${bucket}" \
  --cors-configuration '{"CORSRules":[{"AllowedOrigins":["*"],"AllowedHeaders":["*"],"AllowedMethods":
  ["GET","PUT","POST","DELETE"],"MaxAgeSeconds":3000}]}' >&- || exit
aws s3api put-bucket-notification-configuration \
  --bucket "${bucket}" \
  --notification-configuration "{\"LambdaFunctionConfigurations\":[{\"Id\":\"on-image-upload\",\"LambdaFunctionArn\":
  \"arn:aws:lambda:us-east-1:${id}:function:on-image-upload\",\"Events\":[\"s3:ObjectCreated:Post\"]}]}" >&- || exit

echo "Creating Cognito user pool..."
cognitoPool=$(aws cognito-idp create-user-pool \
  --pool-name simple-chat-users \
  --username-configuration=CaseSensitive=false \
  --policies=PasswordPolicy="{MinimumLength=8,RequireUppercase=false,RequireLowercase=false,RequireNumbers=false,RequireSymbols=false}" \
  --alias-attributes "preferred_username" "email" \
  --schema="Name=email,AttributeDataType=String,DeveloperOnlyAttribute=false,Mutable=true,Required=true" \
  --lambda-config "PostConfirmation=arn:aws:lambda:us-east-1:${id}:function:on-user-confirmed" \
  --query 'UserPool.Id' \
  --output text) || exit
echo "Created user pool: ${cognitoPool}"

echo "Creating user pool client..."
cognitoClient=$(aws cognito-idp create-user-pool-client \
  --user-pool-id "${cognitoPool}" \
  --client-name simple-chat-auth \
  --no-generate-secret \
  --prevent-user-existence-errors "ENABLED" \
  --query "UserPoolClient.ClientId" \
  --output text) || exit
echo "Created client: ${cognitoClient}"

echo "Populating API template IDs..."
cp api-template.yaml api.yaml || exit
sed -i "s/{ID}/${id}/g" api.yaml || exit
sed -i "s/{POOL}/${cognitoPool}/g" api.yaml || exit
sed -i "s/{CLIENT}/${cognitoClient}/g" api.yaml || exit

echo "Creating Gateway API..."
api=$(aws apigatewayv2 import-api \
  --body 'file://api.yaml' \
  --query '[ApiId,ApiEndpoint]' \
  --output json) || exit
rm ./api.yaml
apiId=$(jq -r ".[0]" <<<"${api}")
apiEndpoint=$(jq -r ".[1]" <<<"${api}")
echo "Created API with endpoint: ${apiEndpoint}"

echo "Creating API Stage..."
aws apigatewayv2 create-stage \
  --api-id "${apiId}" \
  --stage-name "\$default" \
  --auto-deploy >&- || exit

echo "Writing API details to client env file..."
echo "api=${apiEndpoint}" >../client/local.env || exit
echo "cognitoPool=${cognitoPool}" >>../client/local.env || exit
echo "cognitoClient=${cognitoClient}" >>../client/local.env || exit

echo "Building Web App..."
(
  cd ../client || exit 1
  quasar build -m pwa >&- || exit 1
  cd ./dist/pwa || exit 1
  zip -qr ../pwa.zip ./* || exit 1
) || exit
echo "Successfully built Web App"

echo "Creating Amplify App..."
amplifyId=$(aws amplify create-app \
  --name simple-chat-app \
  --query "app.appId" \
  --output text) || exit

echo "Creating Amplify branch..."
aws amplify create-branch \
  --app-id "${amplifyId}" \
  --branch-name prod >&- || exit

echo "Creating Amplify deployment..."
uploadUrl=$(aws amplify create-deployment \
  --app-id "${amplifyId}" \
  --branch-name prod \
  --query "zipUploadUrl" \
  --output text) || exit

echo "Uploading Web App..."
curl "${uploadUrl}" \
  --upload-file ../client/dist/pwa.zip || exit
rm ../client/dist/pwa.zip

echo "Deploying Amplify App..."
aws amplify start-deployment \
  --app-id "${amplifyId}" \
  --branch-name prod \
  --job-id 1 >&- || exit
echo "App URL: https://prod.${amplifyId}.amplifyapp.com"

echo "Waiting for database readiness..."
aws dynamodb wait table-exists \
  --table-name simple-chat-users

echo "Creating test users..."
for username in thelogicmaster byteme; do
  aws cognito-idp admin-create-user \
    --user-pool-id "${cognitoPool}" \
    --username "${username}" \
    --temporary-password password \
    --user-attributes "Name=email,Value=example@example.com" >&- || exit
done
aws dynamodb put-item \
  --table-name simple-chat-users \
  --item "{\"username\":{\"S\":\"thelogicmaster\"},\"friends\":{\"L\":[{\"S\":\"byteme\"}]}}" || exit
aws dynamodb put-item \
  --table-name simple-chat-users \
  --item "{\"username\":{\"S\":\"byteme\"},\"friends\":{\"L\":[{\"S\":\"thelogicmaster\"}]}}" || exit
echo "Created users 'thelogicmaster' and 'byteme' with temporary password 'password'"

echo "Successfully created app AWS stack!"
