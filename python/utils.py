"""
utils.py — Helper utilities for Jarvis
"""

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗               ║
║       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝               ║
║       ██║███████║██████╔╝██║   ██║██║███████╗               ║
║  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║               ║
║  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║               ║
║   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝               ║
║                                                              ║
║     Personal AI Assistant  |  Powered by Sarvam AI          ║
║     Windows Desktop Control | Hindi + English + Hinglish    ║
╚══════════════════════════════════════════════════════════════╝
    """)


def speak_startup(sarvam):
    """Play a startup greeting."""
    msg = ("Namaskar Boss! Main Jarvis hoon, aapka personal AI assistant. "
           "Aap mujhse Hindi, English, ya Hinglish mein baat kar sakte hain. "
           "Main aapka computer control kar sakta hoon, files khol sakta hoon, "
           "web search kar sakta hoon, aur bahut kuch. Bataiye, main kya karoon?")
    print(f"\n[Jarvis] {msg}\n")
    try:
        sarvam.text_to_speech(msg)
    except Exception:
        pass