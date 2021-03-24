#!/bin/bash

# Disable need for user intervention for table outputs
export AWS_PAGER=""

echo "Updating Lambda functions..."
for f in *.py; do
  name=${f%.py}
  zip -jq "${name}.zip" "${f}" || exit
  echo "Updating function ${name}..."
  aws lambda update-function-code \
    --function-name "${name}" \
    --zip-file "fileb://${name}.zip" >&- || exit
  rm "${name}.zip"
done
echo "Successfully updated Lambda functions"
