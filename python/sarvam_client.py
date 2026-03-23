"""
sarvam_client.py — Handles all Sarvam AI API calls (STT + TTS)
"""

import os
import base64
import requests
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from config import CONFIG


class SarvamClient:
    BASE_URL = "https://api.sarvam.ai"

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Use consistent headers across all methods
        self.headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }

    # ──────────────────────────────────────────────────────────────────
    #  RECORDING
    # ──────────────────────────────────────────────────────────────────
    def record_audio(self, duration: int = 6) -> str:
        """Record from microphone and save as WAV. Returns file path."""
        rate = CONFIG["SAMPLE_RATE"]
        print(f"[🎙] Listening for {duration}s... (Speak now)")

        # Device 1 = Microphone Array (Realtek) — detected on your system
        audio = sd.rec(int(duration * rate), samplerate=rate,
                       channels=1, dtype="int16", device=1)
        sd.wait()

        # Check audio volume
        volume = np.max(np.abs(audio))
        print(f"[🔊] Volume level: {volume}")
        if volume < 50:
            print("[⚠] Very low audio — speak louder or check mic!")

        path = CONFIG["AUDIO_FILE"]
        wav.write(path, rate, audio)
        size = os.path.getsize(path)
        print(f"[✓] Audio saved: {path} ({size} bytes)")
        return path

    # ──────────────────────────────────────────────────────────────────
    #  SPEECH → TEXT
    # ──────────────────────────────────────────────────────────────────
    def speech_to_text(self, audio_path: str) -> str:
        """Send audio to Sarvam STT and return transcript."""
        url = f"{self.BASE_URL}/speech-to-text"
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            files = {
                "file": ("recording.wav", audio_bytes, "audio/wav"),
            }
            data = {
                "model": "saarika:v2.5",
                "language_code": CONFIG["STT_LANGUAGE"],
            }
            resp = requests.post(url, headers=self.headers,
                                 files=files, data=data, timeout=20)

            if resp.status_code != 200:
                print(f"[STT Error] {resp.status_code}: {resp.text}")
                return ""

            transcript = resp.json().get("transcript", "").strip()
            return transcript

        except Exception as e:
            print(f"[STT Error] {e}")
            return ""

    # ──────────────────────────────────────────────────────────────────
    #  TEXT → SPEECH
    # ──────────────────────────────────────────────────────────────────
    def text_to_speech(self, text: str) -> None:
        """Convert text to speech using Sarvam TTS and play it."""
        url = f"{self.BASE_URL}/text-to-speech"
        # Split long text into chunks (Sarvam TTS max ~500 chars)
        chunks = self._split_text(text, max_len=400)
        for chunk in chunks:
            try:
                payload = {
                    "inputs": [chunk],
                    "target_language_code": CONFIG["TTS_LANGUAGE"],
                    "speaker": CONFIG["TTS_SPEAKER"],
                    "model": "bulbul:v2",
                    "pace": 1.0,
                    "loudness": 1.5,
                    "pitch": 0,
                    "speech_sample_rate": 22050,
                    "enable_preprocessing": True,
                }
                
                # Use consistent headers - no override
                resp = requests.post(url, headers=self.headers,
                                     json=payload, timeout=20)
                
                # Handle different error responses
                if resp.status_code == 400:
                    error_msg = resp.json().get("error", {}).get("message", "Bad request")
                    print(f"[TTS Error] 400: {error_msg}")
                    raise Exception(f"TTS API 400: {error_msg}")
                elif resp.status_code != 200:
                    print(f"[TTS Error] {resp.status_code}: {resp.text}")
                    raise Exception(f"TTS API error: {resp.status_code}")
                
                audio_b64 = resp.json()["audios"][0]
                audio_bytes = base64.b64decode(audio_b64)

                out_path = CONFIG["OUTPUT_AUDIO"]
                with open(out_path, "wb") as f:
                    f.write(audio_bytes)
                self._play_wav(out_path)

            except Exception as e:
                print(f"[TTS Error] {e}")
                # Fallback: use Windows built-in TTS
                self._fallback_tts(text)

    def _play_wav(self, path: str) -> None:
        """Play a WAV file through speakers."""
        try:
            rate, data = wav.read(path)
            sd.play(data, rate)
            sd.wait()
        except Exception as e:
            print(f"[Playback Error] {e}")

    def _split_text(self, text: str, max_len: int = 400):
        """Split text into sentence-aware chunks."""
        if len(text) <= max_len:
            return [text]
        chunks, current = [], ""
        for sentence in text.replace("।", ".").split("."):
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current) + len(sentence) < max_len:
                current += sentence + ". "
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence + ". "
        if current:
            chunks.append(current.strip())
        return chunks or [text[:max_len]]

    def _fallback_tts(self, text: str) -> None:
        """Windows built-in TTS fallback using PowerShell."""
        safe = text.replace("'", "").replace('"', "")
        os.system(f'powershell -Command "Add-Type -AssemblyName System.Speech; '
                  f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{safe}\')"')

    def _fallback_tts_enhanced(self, text: str) -> None:
        """Enhanced Windows TTS with better error handling."""
        try:
            import win32com.client
            speak = win32com.client.Dispatch("SAPI.SpVoice")
            speak.Speak(text)
        except ImportError:
            # Fallback to PowerShell if win32com not available
            self._fallback_tts(text)
        except Exception as e:
            print(f"[Enhanced TTS Error] {e}")
            self._fallback_tts(text)
