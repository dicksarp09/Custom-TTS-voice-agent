# AWS Lambda Deployment Guide - SiriusMed Voice Agent

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with Lambda access
2. **AWS CLI** installed and configured
3. **IAM Role** with Lambda execution permissions
4. **LiveKit Credentials** (URL, API Key, API Secret)

## Step-by-Step Deployment

### Step 1: Create Lambda Function in AWS Console

1. Go to **AWS Lambda Console** → https://console.aws.amazon.com/lambda
2. Click **Create Function**
3. Configure:
   - **Function Name**: `siriusmed-voice-agent`
   - **Runtime**: `Python 3.11`
   - **Architecture**: `x86_64` (or `arm64` for cost savings)
   - **Execution Role**: Create a new role with basic Lambda execution permissions
4. Click **Create Function**

### Step 2: Set Environment Variables

In Lambda console, go to **Configuration** → **Environment Variables**

Add these variables:

```
LIVEKIT_URL = wss://your-instance.livekit.cloud
LIVEKIT_API_KEY = your_api_key_here
LIVEKIT_API_SECRET = your_api_secret_here
```

### Step 3: Increase Timeout & Memory

In Lambda console, go to **Configuration** → **General Configuration**

Change:
- **Memory**: `3008 MB` (maximum for better performance)
- **Timeout**: `5 minutes` (300 seconds)

**Why?** VoxCPM model loading takes time. More memory = faster CPU.

### Step 4: Upload Code

#### Option A: AWS Console (Simple, for small code)

1. Download the deployment package:
```powershell
cd c:\Workspace\voice_agent

# Create a zip file with your source
Compress-Archive -Path src, lambda_handler.py, pyproject.toml -DestinationPath lambda_deployment.zip
```

2. In Lambda console, click **Upload from** → **Upload a zip file**
3. Select your `lambda_deployment.zip`

#### Option B: AWS CLI (Recommended)

```powershell
cd c:\Workspace\voice_agent

# Build deployment package
mkdir lambda_build
Copy-Item -Path src, lambda_handler.py, pyproject.toml -Destination lambda_build -Recurse

# Create zip
Compress-Archive -Path lambda_build/* -DestinationPath lambda_deployment.zip

# Deploy to Lambda
aws lambda update-function-code `
    --function-name siriusmed-voice-agent `
    --zip-file fileb://lambda_deployment.zip `
    --region us-east-1
```

### Step 5: Add Lambda Layers (Dependencies)

Lambda has file size limits. Use **Lambda Layers** for large dependencies like PyTorch.

#### Create a Layer:

```powershell
# Create layer directory
mkdir -p lambda-layer/python/lib/python3.11/site-packages

# Install dependencies
pip install -t lambda-layer/python/lib/python3.11/site-packages `
    livekit-agents `
    livekit-agents-google `
    torch `
    numpy

# Zip the layer
Compress-Archive -Path lambda-layer/* -DestinationPath lambda-layer.zip

# Create the layer
aws lambda publish-layer-version `
    --layer-name siriusmed-dependencies `
    --zip-file fileb://lambda-layer.zip `
    --compatible-runtimes python3.11 `
    --region us-east-1
```

Then in Lambda console:
1. Go to **Layers** section
2. Click **Add layer**
3. Select the layer you just created

### Step 6: Test the Function

#### Via AWS Console:
1. Click **Test**
2. Create a test event (empty JSON is fine)
3. Click **Test**
4. Check logs in **CloudWatch**

#### Via AWS CLI:
```powershell
aws lambda invoke `
    --function-name siriusmed-voice-agent `
    --region us-east-1 `
    response.json

cat response.json
```

### Step 7: Connect to LiveKit

Your agent will automatically:
1. Connect to LiveKit via WebSocket using `LIVEKIT_URL`
2. Register as a worker
3. Wait for incoming calls
4. Join rooms and speak

To test:
1. Go to LiveKit Cloud console
2. Create a room
3. Click **Open in Playground**
4. Agent should join automatically

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Add missing module to Lambda Layer

```powershell
pip install -t lambda-layer/python/lib/python3.11/site-packages voxcpm
```

### Issue: Timeout error (12 seconds)

**Solution**: Increase timeout in Lambda Configuration to 300 seconds

### Issue: "Out of Memory" error

**Solution**: Increase memory to 3008 MB in Lambda Configuration

### Issue: Agent not connecting to LiveKit

**Solution**: Check environment variables in Lambda console - they must match exactly.

## Monitoring

Monitor your Lambda function:

```powershell
# View recent logs
aws logs tail /aws/lambda/siriusmed-voice-agent --follow

# Get function details
aws lambda get-function --function-name siriusmed-voice-agent
```

## Cost Estimation

For moderate usage:
- **Compute**: ~$0.20 per million invocations
- **Data transfer**: ~$0.09 per GB out
- **Memory allocation**: Charged per 100ms of execution

With 100 calls/day at 10 seconds each:
- ~$3-5/month

## Next Steps

1. ✅ Create Lambda function
2. ✅ Set environment variables
3. ✅ Upload code
4. ✅ Test with LiveKit Playground
5. Optional: Set up CloudWatch alarms
6. Optional: Add API Gateway for HTTP webhooks

---

**Need help?** Check the AWS Lambda documentation: https://docs.aws.amazon.com/lambda/
