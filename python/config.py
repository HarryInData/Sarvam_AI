import os

CONFIG = {
    "SARVAM_API_KEY": os.getenv("SARVAM_API_KEY", ""),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "gemini"),
    "LLM_MODEL": os.getenv("LLM_MODEL", "gemini-1.5-flash"),

    # Alias used by some Sarvam SDK integrations.
    "API_KEY": os.getenv("SARVAM_API_KEY", ""),
    "STT_LANGUAGE": os.getenv("STT_LANGUAGE", "hi-IN"),
    "STT_MODEL": os.getenv("STT_MODEL", "saaras:v3"),
    "STT_MODE": os.getenv("STT_MODE", "transcribe"),

    "TTS_LANGUAGE": os.getenv("TTS_LANGUAGE", "hi-IN"),
    "TTS_SPEAKER": os.getenv("TTS_SPEAKER", "anushka"),
    "TTS_MODEL": os.getenv("TTS_MODEL", "bulbul:v2"),

    "RECORD_SECONDS": int(os.getenv("RECORD_SECONDS", "6")),
    "SAMPLE_RATE": int(os.getenv("SAMPLE_RATE", "16000")),
    "AUDIO_FILE": os.getenv("AUDIO_FILE", "temp_input.wav"),
    "OUTPUT_AUDIO": os.getenv("OUTPUT_AUDIO", "temp_output.wav"),
    "REQUIRE_WAKE_WORD": os.getenv("REQUIRE_WAKE_WORD", "false").lower() == "true",
    "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS", ""),
    "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD", ""),
    "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
    "DEFAULT_BROWSER": os.getenv("DEFAULT_BROWSER", "chrome"),
    "JARVIS_NAME": os.getenv("JARVIS_NAME", "Jarvis"),
    "USER_NAME": os.getenv("USER_NAME", "Boss"),
}
