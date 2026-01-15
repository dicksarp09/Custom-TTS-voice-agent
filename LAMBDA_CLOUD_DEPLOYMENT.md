# Lambda Cloud Deployment Guide - SiriusMed Voice Agent

## What is Lambda Cloud?

Lambda Cloud is a GPU cloud provider. Perfect for your agent because:
- VoxCPM runs 10-100x faster on GPU (H100, A100, RTX6000)
- No cold starts
- Simple Linux/Docker deployment
- Pay $0.50-2.50/hour for GPUs

## Prerequisites

1. **Lambda Cloud Account** - https://lambdalabs.com
2. **SSH Key** - For connecting to instances
3. **LiveKit Credentials**
4. **GPU Instance** - Rent from Lambda Cloud dashboard

## Step 1: Create & Launch a Lambda Cloud Instance

### 1.1 Sign up at https://lambdalabs.com

### 1.2 Go to Dashboard → **Launch Instance**

Configure:
- **GPU Type**: Select one (recommended: A100, H100, or RTX6000)
- **Region**: Choose nearest to your location
- **Name**: `siriusmed-agent`
- **Instance Type**: 1x GPU is enough
- Click **Launch**

Wait 2-3 minutes for instance to start.

### 1.3 Get Connection Details

After launch, you'll see:
```
IP Address: 123.45.67.89
SSH Command: ssh ubuntu@123.45.67.89
```

Save these!

## Step 2: Connect to Your Instance

```powershell
# On Windows, use your SSH key
ssh -i your_key.pem ubuntu@123.45.67.89

# Or use WSL/Git Bash
ssh ubuntu@123.45.67.89
```

You should see a Linux prompt:
```
ubuntu@instance-name:~$
```

## Step 3: Clone Your Code

```bash
# Install git
sudo apt-get update && sudo apt-get install -y git

# Clone your repository (or upload your files)
git clone https://github.com/YOUR_REPO/voice_agent.git
cd voice_agent

# Or upload via SCP
# On your local machine:
# scp -r c:\Workspace\voice_agent ubuntu@123.45.67.89:/home/ubuntu/
```

## Step 4: Install Dependencies

```bash
# Install Python and UV
sudo apt-get install -y python3.11 python3-pip

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Navigate to your project
cd voice_agent

# Install dependencies
uv sync
```

## Step 5: Verify GPU is Available

```bash
# Check GPU
nvidia-smi

# Should show something like:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.00    Driver Version: 535.00       CUDA Version: 12.2       |
# +-----------------------------------------------------------------------------+
# | GPU Name          Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | No running processes found                                                  |
# +-------------------------------+----------------------+-----------------------+
```

## Step 6: Set Environment Variables

```bash
# Create .env file
cat > .env << EOF
LIVEKIT_URL=wss://siriusmed-voice-assistant-p9nt01a3.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
EOF

# Verify
cat .env
```

## Step 7: Run Your Agent

```bash
# Run the agent
uv run python src/siriusmed_gemini_agent.py

# You should see:
# Loading VoxCPM model: dicksonsarpong9/voxcpm_nigeria_accent on cuda...
# registered worker
# HTTP server listening on :50103
```

Congratulations! Your agent is now running on GPU! 🎉

## Step 8: Keep Agent Running (Detach from SSH)

To keep the agent running after disconnecting from SSH:

### Option A: Use `screen` (simple)

```bash
# Start a new screen session
screen -S agent

# Inside screen, run your agent
uv run python src/siriusmed_gemini_agent.py

# Press Ctrl+A then D to detach
# Reconnect later:
screen -r agent
```

### Option B: Use `tmux` (better)

```bash
# Start tmux session
tmux new-session -d -s agent

# Run agent in background
tmux send-keys -t agent "cd voice_agent && uv run python src/siriusmed_gemini_agent.py" Enter

# View logs
tmux capture-pane -t agent -p

# Reconnect
tmux attach -t agent
```

### Option C: Use `systemd` (production)

```bash
# Create systemd service
sudo tee /etc/systemd/system/siriusmed-agent.service > /dev/null << EOF
[Unit]
Description=SiriusMed Voice Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/voice_agent
ExecStart=/home/ubuntu/.local/bin/uv run python src/siriusmed_gemini_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable siriusmed-agent
sudo systemctl start siriusmed-agent

# View logs
sudo journalctl -u siriusmed-agent -f
```

## Step 9: Test the Agent

From your local machine:

```powershell
# Run the test script
cd c:\Workspace\voice_agent
uv run python test_agent_call.py

# Or manually:
# 1. Go to https://cloud.livekit.io
# 2. Create a room
# 3. Open in Playground
# 4. Agent should join and speak (FAST on GPU!)
```

## Step 10: Monitor Your Instance

### Check agent is running:
```bash
# SSH into instance
ssh ubuntu@123.45.67.89

# View agent logs
tail -f /tmp/agent.log  # if you redirected output

# Or check process
ps aux | grep python
```

### Monitor GPU usage:
```bash
# Watch GPU in real-time
watch -n 1 nvidia-smi

# Or use GPU monitoring
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits
```

## Cost Breakdown

### Lambda Cloud Pricing (as of Jan 2026)

| GPU | Price/hour | Monthly (24/7) |
|-----|-----------|-----------------|
| RTX 6000 Ada | $1.99 | ~$1,500 |
| A100 80GB | $2.49 | ~$1,870 |
| H100 | $3.49 | ~$2,630 |
| RTX 4090 | $0.74 | ~$560 |
| RTX 6000 | $1.29 | ~$980 |

**For testing:** RTX 6000 (~$1/hour) is more than enough
**For production:** A100 or H100

### Your actual cost:
- If running 8 hours/day: ~$250-500/month for RTX 6000
- If running 24/7: ~$600-1,000/month for RTX 6000

## Stopping Your Instance

When done testing:

```bash
# From Lambda Cloud Dashboard
# Click instance → "Stop Instance"
# Cost stops accumulating immediately!

# To delete completely:
# Click instance → "Terminate Instance"
```

## Troubleshooting

### Issue: "CUDA not available"
```bash
# Check drivers
nvidia-smi

# If missing, install CUDA
sudo apt-get install -y nvidia-driver-535 cuda-toolkit
```

### Issue: "Out of memory"
```bash
# Check available GPU memory
nvidia-smi

# If full, restart the agent or upgrade GPU
```

### Issue: "Connection refused" (can't connect to LiveKit)
```bash
# Check internet connectivity
ping 8.8.8.8

# Check firewall allows outbound connections
# Lambda Cloud instances have outbound access by default
```

### Issue: Agent disconnects after SSH disconnect
**Solution**: Use `screen`, `tmux`, or `systemd` (see Step 8)

## Next Steps

1. ✅ Create Lambda Cloud account
2. ✅ Launch GPU instance
3. ✅ Clone your code
4. ✅ Run agent on GPU
5. ✅ Keep it running with screen/tmux/systemd
6. Test with LiveKit Playground
7. Monitor performance & costs
8. Scale up if needed (add more instances)

## Need Help?

- Lambda Cloud Docs: https://lambdalabs.com/
- LiveKit Docs: https://docs.livekit.io/
- SSH Troubleshooting: https://lambdalabs.com/support

---

**TL;DR Quick Setup:**
```bash
# 1. Create instance on lambdalabs.com
# 2. SSH in
# 3. Clone code & install dependencies
# 4. Set .env with LiveKit credentials
# 5. Run: uv run python src/siriusmed_gemini_agent.py
# 6. Test with LiveKit Playground
# 7. Use screen/tmux to keep running
# 8. Stop instance when done
```
