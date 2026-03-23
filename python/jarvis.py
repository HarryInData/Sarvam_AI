"""
╔══════════════════════════════════════════════════════╗
║         J.A.R.V.I.S - Personal AI Assistant          ║
║     Built with Sarvam AI | Windows Desktop Control   ║
╚══════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import threading
import json
from config import CONFIG

# Use local voice instead of Sarvam
from local_voice import LocalVoiceClient
from brain import JarvisBrain
from desktop_controller import DesktopController
from utils import speak_startup, print_banner
from avatar import AvatarWindow

def assistant_thread(avatar):
    print_banner()
    
    # Initialize all modules
    print("[*] Initializing Jarvis modules...")
    voice = LocalVoiceClient(avatar=avatar)

    # Pick the right API key based on provider chosen in config
    provider = CONFIG.get("LLM_PROVIDER", "openai")
    if provider == "gemini":
        llm_key = CONFIG.get("GEMINI_API_KEY", "")
    else:
        llm_key = CONFIG.get("OPENAI_API_KEY", "")
    brain = JarvisBrain(llm_key)
    desktop = DesktopController()

    speak_startup(voice)

    print("[✓] Jarvis is ONLINE. Say something!\n")

    while True:
        try:
            # ── 1. LISTEN ──────────────────────────────────────────────
            audio_path = voice.record_audio(duration=CONFIG["RECORD_SECONDS"])

            # ── 2. SPEECH → TEXT ─────────────────────────
            transcript = voice.speech_to_text(audio_path)
            if not transcript or len(transcript.strip()) < 2:
                continue
            print(f"\n[You] {transcript}")

            # ── 3. WAKE WORD CHECK ─────────────────────────────────────
            wake_words = ["jarvis", "hey jarvis", "yo jarvis", "hello jarvis"]
            if CONFIG.get("REQUIRE_WAKE_WORD", False):
                lower = transcript.lower()
                if not any(w in lower for w in wake_words):
                    continue  # silently ignore non-commands

            # ── 4. PROCESS WITH AI BRAIN ───────────────────────────────
            response = brain.process(transcript, desktop)

            # ── 5. TEXT → SPEECH ─────────────────────────
            print(f"[Jarvis] {response['text']}")
            voice.text_to_speech(response["text"])

        except KeyboardInterrupt:
            print("\n[*] Jarvis shutting down. Goodbye!")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(1)

def main():
    # Initialize the Pygame Avatar window on the main thread
    app = AvatarWindow(width=800, height=600)
    
    # Start the assistant logic in a background daemon thread
    t = threading.Thread(target=assistant_thread, args=(app,), daemon=True)
    t.start()
    
    # Run the pygame event loop (blocking, must be in main thread)
    app.run()

if __name__ == "__main__":
    main()