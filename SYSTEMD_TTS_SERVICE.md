# SiriusMed TTS Server Systemd Service

To deploy the TTS server as a systemd service on Lambda Cloud, run these commands on the Ubuntu instance:

## Step 1: Create the systemd service file

```bash
sudo tee /etc/systemd/system/siriusmed-tts.service > /dev/null << 'EOF'
[Unit]
Description=SiriusMed TTS Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Custom-TTS-voice-agent
ExecStart=/home/ubuntu/Custom-TTS-voice-agent/.venv/bin/python src/tts_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

## Step 2: Reload systemd daemon

```bash
sudo systemctl daemon-reload
```

## Step 3: Enable the TTS service (auto-start on boot)

```bash
sudo systemctl enable siriusmed-tts
```

## Step 4: Start the TTS service

```bash
sudo systemctl start siriusmed-tts
```

## Step 5: Check TTS service status

```bash
sudo systemctl status siriusmed-tts
```

## Step 6: View TTS service logs

```bash
sudo journalctl -u siriusmed-tts -f --no-pager
```

## Step 7: Restart the LiveKit agent service (if already running)

```bash
sudo systemctl restart siriusmed-agent
```

## Verification

After both services are running, check they are both active:

```bash
sudo systemctl status siriusmed-tts siriusmed-agent
```

You should see:
- `siriusmed-tts`: Active (running)
- `siriusmed-agent`: Active (running)

The TTS server will start, load the model once, and stay warm. The voice agent will start instantly and connect to the TTS server on demand.
