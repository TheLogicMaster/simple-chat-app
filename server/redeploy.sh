#!/bin/bash

echo "Destroying existing AWS stack"
./destroy.sh || exit
echo "Successfully destroyed AWS stack"

echo "Deploying new AWS stack"
./deploy.sh || exit
echo "Successfully redeployed AWS stack"