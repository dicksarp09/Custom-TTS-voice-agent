# Environment Configuration for SiriusMed Voice Agent

The following environment variables should be set in a `.env` file in the project root:

## Required Variables

### LiveKit Configuration
```
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

### Google Gemini API
```
GOOGLE_API_KEY=your-google-api-key
```

### TTS Server (Optional)
```
TTS_SERVER_URL=ws://127.0.0.1:9001
```

If `TTS_SERVER_URL` is not set, it defaults to `ws://127.0.0.1:9001`.

## Notes

- Keep `.env` out of version control (already excluded in `.gitignore`)
- The TTS server must be running before starting the voice agent
- On Lambda Cloud, both services run as systemd services managed independently
- The voice agent is lightweight and starts in seconds
- The TTS server loads the model once and stays warm
