import os
import wave
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav_write
from config import CONFIG
import pyttsx3

try:
    from faster_whisper import WhisperModel
    _WHISPER_AVAILABLE = True
except ImportError:
    _WHISPER_AVAILABLE = False

class LocalVoiceClient:
    """Handles STT with fast-whisper and TTS with pyttsx3, 
    with Avatar lip-sync integration."""
    def __init__(self, avatar=None):
        self.avatar = avatar
        
        # Initialize COM for Windows background thread
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pass
            
        # Initialize TTS
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 160)
        self.tts.setProperty('volume', 1.0)
        
        # Initialize STT
        if _WHISPER_AVAILABLE:
            print("[*] Loading Faster-Whisper model... (This might take a moment)")
            self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
            print("[*] Faster-Whisper loaded.")
        else:
            self.model = None
            print("[!] Faster-Whisper is not installed. STT won't work locally.")
            
    def record_audio(self, duration=6):
        rate = CONFIG["SAMPLE_RATE"]
        if self.avatar:
            self.avatar.set_state("listening")
            
        print(f"[🎙] Listening for {duration}s... (Speak now)")
        
        audio = sd.rec(int(duration * rate), samplerate=rate, channels=1, dtype="int16")
        sd.wait()
        
        path = CONFIG["AUDIO_FILE"]
        wav_write.write(path, rate, audio)
        print(f"[✓] Audio saved: {path}")
        
        if self.avatar:
            self.avatar.set_state("processing")
            
        return path
        
    def speech_to_text(self, audio_path):
        if not self.model:
            print("[!] Missing Whisper. Empty transcript.")
            return ""
            
        segments, _ = self.model.transcribe(audio_path, beam_size=5)
        text = "".join(segment.text for segment in segments)
        return text.strip()
        
    def text_to_speech(self, text):
        out_path = "tts_output.wav"
        
        # Save TTS to audio file so we can read it back for volume syncing
        self.tts.save_to_file(text, out_path)
        self.tts.runAndWait()
        
        self._play_and_sync(out_path)
        
    def _play_and_sync(self, path):
        """Plays the audio while calculating volume peaks for the avatar."""
        if not os.path.exists(path):
            return
            
        try:
            wf = wave.open(path, 'rb')
            rate = wf.getframerate()
            channels = wf.getnchannels()
            
            frames = wf.readframes(wf.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            if self.avatar:
                self.avatar.set_state("speaking", 0.0)
                
            current_idx = 0
            def callback(outdata, frames, time_info, status):
                nonlocal current_idx
                end_idx = current_idx + frames * channels
                
                # Check for end of file
                if current_idx >= len(audio_data):
                    outdata.fill(0)
                    raise sd.CallbackStop()
                    
                chunk = audio_data[current_idx:end_idx]
                if len(chunk) < frames * channels:
                    padded = np.zeros(frames * channels, dtype=np.int16)
                    padded[:len(chunk)] = chunk
                    outdata[:] = padded.reshape(-1, channels)
                    raise sd.CallbackStop()
                else:
                    outdata[:] = chunk.reshape(-1, channels)
                    
                # Calculate volume (0.0 to 1.0) and send to avatar
                peak = np.max(np.abs(chunk))
                vol = float(peak) / 32768.0
                if self.avatar:
                    self.avatar.set_state("speaking", vol)
                    
                current_idx = end_idx
                
            # Start continuous streaming
            with sd.OutputStream(samplerate=rate, channels=channels, dtype='int16', callback=callback):
                # Calculate required sleep duration based on audio length
                duration_ms = (len(audio_data) / channels / rate) * 1000
                sd.sleep(int(duration_ms) + 100)
                
            if self.avatar:
                self.avatar.set_state("idle", 0.0)
                
        except Exception as e:
            print(f"[Playback Error] {e}")
            if self.avatar:
                self.avatar.set_state("idle", 0.0)
