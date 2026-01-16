"""
SiriusMed TTS Server
====================
Standalone WebSocket server for VoxCPM Nigerian-accent TTS.
Loads model once at startup, stays warm, accepts text, returns audio chunks.
"""

import asyncio
import json
import logging
import os
import sys

import numpy as np
import torch
import websockets
from dotenv import load_dotenv

# Disable symlinks on Windows to avoid permission errors
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

from voxcpm import VoxCPM
from voxcpm.model.voxcpm import VoxCPMModel, LoRAConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monkeypatch VoxCPM to fix a bug in version 1.5.0 where warm-up runs even if optimize=False
def patched_voxcpm_init(self, voxcpm_model_path, zipenhancer_model_path="iic/speech_zipenhancer_ans_multiloss_16k_base", 
                       enable_denoiser=True, optimize=True, lora_config=None, lora_weights_path=None):
    if lora_weights_path is not None and lora_config is None:
        lora_config = LoRAConfig(enable_lm=True, enable_dit=True, enable_proj=False)
    
    self.tts_model = VoxCPMModel.from_local(voxcpm_model_path, optimize=optimize, lora_config=lora_config)
    
    if lora_weights_path is not None:
        self.tts_model.load_lora_weights(lora_weights_path)
    
    self.text_normalizer = None
    if enable_denoiser and zipenhancer_model_path is not None:
        try:
            from voxcpm.zipenhancer import ZipEnhancer
            self.denoiser = ZipEnhancer(zipenhancer_model_path)
        except Exception:
            logger.warning("Failed to load denoiser, proceeding without it.")
            self.denoiser = None
    else:
        self.denoiser = None
        
    if optimize:
        logger.info("Warming up VoxCPMModel...")
        try:
            self.tts_model.generate(target_text="Warmup", max_len=5)
        except Exception as e:
            logger.warning(f"VoxCPM warm-up failed: {e}. Proceeding...")

VoxCPM.__init__ = patched_voxcpm_init

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_ID = "dicksonsarpong9/voxcpm_nigeria_accent"
SAMPLE_RATE = 24000

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# Load model at module level (once at startup)
logger.info(f"Loading VoxCPM model: {MODEL_ID} on {DEVICE}...")
tts_model = None

try:
    tts_model = VoxCPM.from_pretrained(MODEL_ID, optimize=False)
    
    if hasattr(tts_model, "to"):
        tts_model.to(DEVICE)
    
    if DEVICE == "cpu":
        tts_model.tts_model.float()
        
    if hasattr(tts_model, "tts_model"):
        tts_model.tts_model.eval()
        for p in tts_model.tts_model.parameters():
            p.requires_grad = False

    logger.info(f"✓ VoxCPM model loaded on {DEVICE}")
except Exception as e:
    logger.error(f"Failed to load VoxCPM model: {e}")
    logger.info("Falling back to base model openbmb/VoxCPM-0.5B...")
    try:
        tts_model = VoxCPM.from_pretrained("openbmb/VoxCPM-0.5B", optimize=False)
        if DEVICE == "cpu":
            tts_model.tts_model.float()
        if hasattr(tts_model, "tts_model"):
            tts_model.tts_model.eval()
            for p in tts_model.tts_model.parameters():
                p.requires_grad = False
        logger.info("✓ Fallback model loaded")
    except Exception as fallback_e:
        logger.critical(f"Failed to load fallback model: {fallback_e}")
        sys.exit(1)

if tts_model is None:
    logger.critical("Failed to initialize TTS model")
    sys.exit(1)


async def synthesize_text(text: str) -> bytes:
    """Synthesize text to speech and return audio bytes."""
    try:
        with torch.inference_mode():
            wav = tts_model.generate(
                text=text,
                cfg_value=1.5,
                inference_timesteps=6,
                normalize=False,
                denoise=False,
                retry_badcase=False,
            )

        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()

        if len(wav.shape) > 1:
            wav = wav.squeeze()

        if wav.dtype == np.float32 or wav.dtype == np.float64:
            wav_max = np.abs(wav).max()
            if wav_max > 1.0:
                wav = wav / wav_max

        audio_int16 = (wav * 32767).astype(np.int16)
        return audio_int16.tobytes()

    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        raise


async def handle_client(websocket, path):
    """Handle incoming WebSocket connections."""
    logger.info(f"Client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                text = data.get("text", "").strip()

                if not text:
                    await websocket.send(json.dumps({"error": "Empty text"}))
                    continue

                logger.info(f"Synthesizing: {text[:50]}...")
                audio_bytes = await synthesize_text(text)
                
                # Send audio as binary
                await websocket.send(audio_bytes)
                logger.info(f"Sent {len(audio_bytes)} bytes of audio")

            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                await websocket.send(json.dumps({"error": str(e)}))

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected from {websocket.remote_address}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def main():
    """Start the TTS WebSocket server."""
    port = 9001
    logger.info(f"Starting TTS WebSocket server on ws://0.0.0.0:{port}")
    
    async with websockets.serve(handle_client, "0.0.0.0", port):
        logger.info("✓ TTS Server ready and listening")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down TTS server...")
