import torch
import numpy as np
from livekit import rtc
from livekit.agents.tts import TTS

class SparkTTSEngine(TTS):
    def __init__(self, model, sample_rate=24000):
        super().__init__(capabilities=None) # Call super class if needed, checking standard init
        self.model = model
        self.sample_rate = sample_rate

    async def synthesize(self, text: str):
        # Generate waveform from SparkTTS
        with torch.no_grad():
            audio = self.model.infer(text)  # shape: (T,) float32

        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()

        # Convert float32 [-1,1] → int16
        audio_int16 = (audio * 32767).astype(np.int16)

        frame = rtc.AudioFrame(
            data=audio_int16.tobytes(),
            sample_rate=self.sample_rate,
            num_channels=1,
            samples_per_channel=len(audio_int16),
        )

        yield frame
