"""
brain.py — The AI brain of Jarvis.
Sends user commands to LLM with a system prompt that understands
desktop control intents, then calls the right DesktopController method.
"""

import json
import re
from config import CONFIG
from desktop_controller import DesktopController

# ── Try to import OpenAI or Gemini ───────────────────────────────────
try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False


SYSTEM_PROMPT = """
You are Jarvis, a smart personal AI assistant for Windows. 
The user speaks in Hindi, English, or Hinglish (mix of both).
You understand all three languages perfectly.

Your job:
1. Understand the user's intent
2. Return a JSON response with two keys:
   - "action": one of the action codes below (string)
   - "params": a dict of parameters for that action
   - "text": a friendly spoken response (in the same language the user used)

## Available Actions:

### APPS
- open_app       → params: {"app": "chrome"/"notepad"/"calculator"/"vlc"/etc.}
- close_app      → params: {"app": "chrome"/"notepad"/etc.}
- minimize_all   → params: {}
- screenshot     → params: {"filename": "screenshot.png"}

### FILES & FOLDERS
- open_file      → params: {"path": "C:/Users/..."}
- open_folder    → params: {"path": "C:/Users/..."}
- create_file    → params: {"path": "C:/...", "content": "..."}
- delete_file    → params: {"path": "C:/..."}
- search_files   → params: {"query": "filename", "location": "C:/Users"}

### WEB
- web_search     → params: {"query": "search term"}
- open_url       → params: {"url": "https://..."}
- youtube_search → params: {"query": "song or video name"}

### SYSTEM
- volume_up      → params: {}
- volume_down    → params: {}
- mute           → params: {}
- sleep_pc       → params: {}
- restart_pc     → params: {}
- shutdown_pc    → params: {}
- lock_pc        → params: {}
- battery_status → params: {}
- get_time       → params: {}
- get_date       → params: {}
- type_text      → params: {"text": "text to type"}
- press_key      → params: {"key": "ctrl+c"/"ctrl+v"/"enter"/etc.}
- clipboard_copy → params: {"text": "text to copy"}

### EMAIL
- send_email     → params: {"to": "email@example.com", "subject": "...", "body": "..."}

### CONVERSATION
- chat           → params: {"reply": "..."} (for greetings, questions, jokes, etc.)

## Rules:
- Always return valid JSON only, no markdown, no extra text.
- "text" should sound natural and friendly, like Iron Man's Jarvis.
- Mix Hindi/English naturally in "text" based on how user spoke.
- For dangerous actions (delete, shutdown, restart), confirm with user first — set action to "confirm_needed" and explain.
- Never make up file paths. Ask user to specify if unclear.
"""


class JarvisBrain:
    def __init__(self, api_key: str):
        self.history = []  # conversation memory (last 10 turns)
        provider = CONFIG.get("LLM_PROVIDER", "openai")

        if provider == "openai" and _OPENAI_AVAILABLE:
            self.client  = OpenAI(api_key=api_key)
            self.model   = CONFIG.get("LLM_MODEL", "gpt-4o-mini")
            self._call   = self._openai_call
        elif provider == "gemini" and _GEMINI_AVAILABLE:
            gemini_key = CONFIG.get("GEMINI_API_KEY", api_key)
            genai.configure(api_key=gemini_key)
            self.client  = genai.GenerativeModel("gemini-2.0-flash")
            self._call   = self._gemini_call
        else:
            raise RuntimeError("No LLM provider available. Install openai or google-generativeai.")

    # ──────────────────────────────────────────────────────────────────
    def process(self, user_text: str, desktop: DesktopController) -> dict:
        """Main entry: take user text → decide action → execute → return response."""
        # Add to history
        self.history.append({"role": "user", "content": user_text})
        if len(self.history) > 20:
            self.history = self.history[-20:]

        # Get LLM decision
        raw = self._call(self.history)
        parsed = self._parse_json(raw)

        # Execute action
        action  = parsed.get("action", "chat")
        params  = parsed.get("params", {})
        text    = parsed.get("text", "Haan boss, karta hoon.")

        result_text = self._execute(action, params, desktop, text)

        # Add assistant turn to history
        self.history.append({"role": "assistant", "content": result_text})

        return {"text": result_text, "action": action}

    # ──────────────────────────────────────────────────────────────────
    def _execute(self, action: str, params: dict,
                 desktop: DesktopController, default_text: str) -> str:
        """Route action to DesktopController and return spoken result."""
        try:
            if   action == "open_app":       desktop.open_app(params.get("app",""))
            elif action == "close_app":      desktop.close_app(params.get("app",""))
            elif action == "minimize_all":   desktop.minimize_all()
            elif action == "screenshot":     desktop.take_screenshot(params.get("filename","screenshot.png"))
            elif action == "open_file":      desktop.open_path(params.get("path",""))
            elif action == "open_folder":    desktop.open_path(params.get("path",""))
            elif action == "create_file":    desktop.create_file(params.get("path",""), params.get("content",""))
            elif action == "delete_file":    desktop.delete_file(params.get("path",""))
            elif action == "search_files":   desktop.search_files(params.get("query",""), params.get("location",""))
            elif action == "web_search":     desktop.web_search(params.get("query",""))
            elif action == "open_url":       desktop.open_url(params.get("url",""))
            elif action == "youtube_search": desktop.youtube_search(params.get("query",""))
            elif action == "volume_up":      desktop.volume_up()
            elif action == "volume_down":    desktop.volume_down()
            elif action == "mute":           desktop.mute()
            elif action == "sleep_pc":       desktop.sleep_pc()
            elif action == "restart_pc":     desktop.restart_pc()
            elif action == "shutdown_pc":    desktop.shutdown_pc()
            elif action == "lock_pc":        desktop.lock_pc()
            elif action == "type_text":      desktop.type_text(params.get("text",""))
            elif action == "press_key":      desktop.press_key(params.get("key",""))
            elif action == "clipboard_copy": desktop.clipboard_copy(params.get("text",""))
            elif action == "send_email":     desktop.send_email(params)
            elif action == "battery_status":
                info = desktop.battery_status()
                return info
            elif action == "get_time":
                return desktop.get_time()
            elif action == "get_date":
                return desktop.get_date()

        except Exception as e:
            return f"Sorry boss, ek problem ayi: {e}"

        return default_text

    # ──────────────────────────────────────────────────────────────────
    def _openai_call(self, history: list) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()

    def _gemini_call(self, history: list) -> str:
        prompt = SYSTEM_PROMPT + "\n\nConversation:\n"
        for h in history:
            prompt += f"{h['role'].upper()}: {h['content']}\n"
        prompt += "ASSISTANT (JSON only):"
        resp = self.client.generate_content(prompt)
        return resp.text.strip()

    def _parse_json(self, raw: str) -> dict:
        """Safely parse JSON from LLM output."""
        # Strip markdown code blocks if present
        raw = re.sub(r"```json|```", "", raw).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try extracting JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        return {"action": "chat", "params": {}, "text": raw}