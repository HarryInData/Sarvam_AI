# Sarvam AI Voice Assistant

A Python voice-assistant project with a desktop avatar, local speech recognition and speech output, an AI chat backend, and optional Sarvam AI speech API helpers.

## Configuration

API credentials are read from environment variables. Do not add real keys to source files or commit them.

In PowerShell, set the keys for the current terminal session before launching the project:

```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:OPENAI_API_KEY = "your-openai-api-key"
$env:SARVAM_API_KEY = "your-sarvam-api-key"
```

The project uses `GEMINI_API_KEY` or `OPENAI_API_KEY` according to `LLM_PROVIDER`. The Sarvam client reads `SARVAM_API_KEY`. Configure only the providers you use. Other settings, such as language and recording duration, can also be overridden through environment variables; see `python/config.py`.

## Project layout

- `python/jarvis.py` starts the assistant and its avatar window.
- `python/local_voice.py` handles microphone input, local Whisper transcription, and speech playback.
- `python/brain.py` contains the assistant's AI response logic.
- `python/desktop_controller.py` contains Windows desktop actions.
- `python/sarvam_client.py` contains optional Sarvam speech-to-text and text-to-speech API calls.

This project can control desktop applications and perform system actions. Review the available actions in `python/desktop_controller.py` before running it.
