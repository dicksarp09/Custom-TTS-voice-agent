#!/bin/bash
# AWS Lambda Deployment Script for SiriusMed Agent
# This script builds and deploys the agent to AWS Lambda

set -e

# Configuration
FUNCTION_NAME="siriusmed-voice-agent"
RUNTIME="python3.11"
ROLE_ARN="arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE"
REGION="us-east-1"
TIMEOUT=300  # 5 minutes
MEMORY=3008  # Max memory for better CPU

echo "=========================================="
echo "SiriusMed Agent - Lambda Deployment"
echo "=========================================="

# Step 1: Create deployment package
echo "📦 Creating deployment package..."
mkdir -p lambda_build
cd lambda_build

# Copy source files
cp -r ../src .
cp ../lambda_handler.py .
cp ../pyproject.toml .
cp ../uv.lock .

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r <(pip-compile --dry-run ../pyproject.toml 2>/dev/null || echo "livekit-agents livekit-plugins-google livekit-plugins-openai torch numpy")

# Create zip package
echo "🗜️ Creating zip archive..."
zip -r ../lambda_deployment.zip .
cd ..

# Step 2: Update Lambda function
echo "🚀 Deploying to AWS Lambda..."
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda_deployment.zip \
    --region $REGION

# Step 3: Configure environment variables
echo "⚙️ Setting environment variables..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --runtime $RUNTIME \
    --handler lambda_handler.lambda_handler \
    --timeout $TIMEOUT \
    --memory-size $MEMORY \
    --environment Variables="{LIVEKIT_URL=$(echo $LIVEKIT_URL),LIVEKIT_API_KEY=$(echo $LIVEKIT_API_KEY),LIVEKIT_API_SECRET=$(echo $LIVEKIT_API_SECRET)}" \
    --region $REGION

# Step 4: Test the function
echo "✅ Testing Lambda function..."
aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    response.json

echo "Response:"
cat response.json

# Cleanup
rm -rf lambda_build lambda_deployment.zip

echo "=========================================="
echo "✅ Deployment complete!"
echo "=========================================="
echo "Function Name: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Memory: $MEMORY MB"
echo "Timeout: $TIMEOUT seconds"
