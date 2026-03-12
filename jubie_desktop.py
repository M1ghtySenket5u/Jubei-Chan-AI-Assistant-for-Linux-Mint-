import json
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import Optional

import urllib.request
import urllib.error


API_URL_DEFAULT = "http://127.0.0.1:8000"

# Supported languages for Jubei - language - XX
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ja": "Japanese",
    "es": "Spanish",
    "de": "German",
    "ru": "Russian",
}


class JubeiDesktopApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Project Jubei – Desktop Chat")

        # Sakura-inspired background
        sakura_bg = "#ffe4f2"
        self.root.configure(bg=sakura_bg)

        # Current personality mode: "ninja" or "schoolgirl"
        self.mode = "ninja"
        # Current response language: en, ja, es, de, ru
        self.language = "en"

        # API configuration
        self.api_url = os.getenv("JUBIE_API_URL", API_URL_DEFAULT).rstrip("/")
        self.api_key = os.getenv("JUBIE_API_KEY")

        # Typing / idle state tracking
        self._typing_timer_id: Optional[str] = None
        self._last_user_action_state: str = "greetings"

        # Avatar images per character and state.
        # Expected file layout (place these PNGs in an assets/ folder next to this file):
        #   assets/jubei_greetings.png, assets/jubei_reading.png, assets/jubei_explaining.png,
        #   assets/jubei_idle1.png, assets/jubei_idle2.png, assets/jubei_goodbye.png
        #   assets/komi_*.png, assets/katherine_*.png (same pattern)
        self.avatars: dict[str, dict[str, tk.PhotoImage]] = {}

        self._build_ui()
        self._load_avatars()
        self._show_avatar_state("greetings")
        self._print_system_message(
            "Welcome to Jubei-Chan's desktop chat.\n"
            "- Make sure the HTTP server is running: `python jubie_api.py`.\n"
            "- Current mode: Ninja Mode. Type 'Jubei - transform' to switch personalities.\n"
            "- Type 'Jubei - Switch - Katherine' or 'Jubei - Switch - Komi' for other characters; "
            "'Katherine - Switch - Jubei', 'Komi - Switch - Jubei', "
            "'Katherine - Switch - Komi', or 'Komi - Switch - Katherine' to switch.\n"
            "\n[Opens]\n"
            "- Type 'Open - Krita' to open Krita.\n"
            "- Type 'Open - VLC' to open VLC (installs if missing).\n"
            "- Type 'Open - Oneko' to open Oneko (installs if missing).\n"
            "- Type 'Slice - Oneko' to stop Oneko.\n"
            "- Type 'Open - GNU' to open the GNU Image Manipulation Program (GIMP) (installs if missing).\n"
            "- Type 'Open - Ani-cli' to open ani-cli in a new terminal, and 'Slice - Ani-cli' to stop it.\n"
            "- Type 'Open - Hollywood' to open Hollywood in a new terminal, and 'Slice - Hollywood' to stop it.\n"
            "\n[Easter eggs]\n"
            "- 'Jubei - Tempel', 'Jubei - Tux', 'Jubei - Young Girl', 'Jubei - Kino', 'Jubei - Slice' (stop music).\n"
            "- 'Jubei - Creator' to learn about the creator.\n"
            "- 'Jubei - Mint' opens the Linux Mint website; 'Jubei - Cinnamon' opens the Cinnamon themes website.\n"
        )

        # Intercept window close to play goodbye sequence
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_avatars(self) -> None:
        """Load avatar images for Jubei, Komi, and Katherine if present."""
        base_dir = os.path.join(os.path.dirname(__file__), "assets")
        characters = ("jubei", "komi", "katherine")
        states = ("greetings", "reading", "explaining", "idle1", "idle2", "goodbye")
        for character in characters:
            per_state: dict[str, tk.PhotoImage] = {}
            for state in states:
                path = os.path.join(base_dir, f"{character}_{state}.png")
                if os.path.exists(path):
                    try:
                        per_state[state] = tk.PhotoImage(file=path)
                    except Exception:
                        continue
            if per_state:
                self.avatars[character] = per_state

    def _current_character_key(self) -> str:
        if self.mode == "katherine":
            return "katherine"
        if self.mode == "komi":
            return "komi"
        return "jubei"

    def _show_avatar_state(self, state: str) -> None:
        """Update avatar image according to logical state."""
        self._last_user_action_state = state
        character_key = self._current_character_key()
        char_avatars = self.avatars.get(character_key) or self.avatars.get("jubei", {})
        img = char_avatars.get(state)
        if img is None:
            # Fallback: try idle1/idle2/greetings in order
            for fallback in ("idle1", "idle2", "greetings"):
                img = char_avatars.get(fallback)
                if img is not None:
                    break
        if img is not None and hasattr(self, "avatar_label"):
            self.avatar_label.configure(image=img)
            self.avatar_label.image = img  # keep reference
        )
            "- Type 'Jubei - language - XX' to change language (ja, es, de, ru, en).\n"
            "- Easter eggs (Jubei, Katherine, or Komi): 'Jubei - Tempel', 'Jubei - Tux', "
            "'Jubei - Young', 'Jubei - Kino', 'Jubei - Slice' (stop music).\n"
            "- Easter egg: 'Jubei - Creator' to learn about the creator.\n"
            "- Easter eggs: 'Jubei - Mint' opens the Linux Mint website; "
            "'Jubei - Cinnamon' opens the Cinnamon themes website.\n"
        )

    def _build_ui(self) -> None:
        # Main layout: left conversation, right avatar
        sakura_bg = "#ffe4f2"
        peach_text = "#ffccaa"
        dark_panel = "#3b1024"

        main_frame = tk.Frame(self.root, bg=sakura_bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Conversation area
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            state="disabled",
            height=20,
            bg=dark_panel,
            fg=peach_text,
            insertbackground=peach_text,
            highlightbackground="black",
            highlightthickness=1,
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        # Avatar area on the right
        avatar_frame = tk.Frame(main_frame, width=260, bg=sakura_bg, highlightbackground="black", highlightthickness=1)
        avatar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        avatar_frame.pack_propagate(False)

        self.avatar_label = tk.Label(avatar_frame, bg=sakura_bg)
        self.avatar_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Bottom frame: input + buttons
        bottom = tk.Frame(self.root, bg=sakura_bg)
        bottom.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.entry = tk.Entry(bottom, bg="white", fg="black", highlightbackground="black", highlightthickness=1)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_send)
        self.entry.bind("<Key>", self._on_user_typing)

        send_btn = tk.Button(bottom, text="Send", command=self._on_send)
        send_btn.pack(side=tk.LEFT, padx=(4, 0))

        transform_btn = tk.Button(bottom, text="Jubei - transform", command=self._on_transform)
        transform_btn.pack(side=tk.LEFT, padx=(4, 0))

        switch_btn = tk.Button(bottom, text="Switch character", command=self._on_switch_character)
        switch_btn.pack(side=tk.LEFT, padx=(4, 0))

        # Language dropdown
        self.language_var = tk.StringVar(value="en")
        lang_menu = tk.OptionMenu(
            bottom, self.language_var, *SUPPORTED_LANGUAGES.keys(),
            command=self._on_language_change
        )
        lang_menu.pack(side=tk.LEFT, padx=(4, 0))

        self.mode_label = tk.Label(bottom, text="Mode: ninja", bg=sakura_bg)  # ninja, schoolgirl, or katherine
        self.mode_label.pack(side=tk.LEFT, padx=(8, 0))
        self.lang_label = tk.Label(bottom, text="Lang: en", bg=sakura_bg)
        self.lang_label.pack(side=tk.LEFT, padx=(8, 0))

    def _append_text(self, prefix: str, text: str) -> None:
        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, f"{prefix}{text}\n\n")
        self.text_area.see(tk.END)
        self.text_area.configure(state="disabled")

    def _print_system_message(self, msg: str) -> None:
        self._append_text("[System] ", msg)

    def _on_send(self, event=None) -> None:  # type: ignore[override]
        message = self.entry.get().strip()
        if not message:
            return
        self._show_avatar_state("reading")
        self.entry.delete(0, tk.END)
        self._append_text("[You] ", message)
        threading.Thread(target=self._send_message, args=(message,), daemon=True).start()

    def _on_user_typing(self, event=None) -> None:  # type: ignore[override]
        # Whenever the user types, show the reading state and restart idle timer.
        self._show_avatar_state("reading")
        if self._typing_timer_id is not None:
            try:
                self.root.after_cancel(self._typing_timer_id)
            except Exception:
                pass
        self._typing_timer_id = self.root.after(20000, self._switch_to_idle)

    def _switch_to_idle(self) -> None:
        # Alternate between idle1 and idle2 if available.
        next_state = "idle2" if self._last_user_action_state == "idle1" else "idle1"
        self._show_avatar_state(next_state)
        self._typing_timer_id = None

    def _on_transform(self) -> None:
        # Just send the special transform message with previous personality.
        self._append_text("[You] ", "Jubei - transform")
        threading.Thread(
            target=self._send_transform,
            args=("Jubei - transform",),
            daemon=True,
        ).start()

    def _on_switch_character(self) -> None:
        """Cycle character: Jubei -> Katherine -> Komi -> Jubei."""
        if self.mode == "katherine":
            cmd = "Katherine - Switch - Komi"
        elif self.mode == "komi":
            cmd = "Komi - Switch - Jubei"
        else:
            cmd = "Jubei - Switch - Katherine"
        self._append_text("[You] ", cmd)
        threading.Thread(target=self._send_message, args=(cmd,), daemon=True).start()

    def _on_language_change(self, abbrev: str) -> None:
        self.language = abbrev
        self._update_lang_label()
        # Optionally send the language command to the API for consistency
        self._append_text("[You] ", f"Jubei - language - {abbrev}")
        threading.Thread(
            target=self._send_language_change,
            args=(abbrev,),
            daemon=True,
        ).start()

    def _update_lang_label(self) -> None:
        self.lang_label.configure(text=f"Lang: {self.language}")

    def _send_language_change(self, abbrev: str) -> None:
        payload = {
            "message": f"Jubei - language - {abbrev}",
        }
        resp = self._post_json("/chat", payload)
        if not resp:
            return
        if resp.get("language_change"):
            self.language = resp.get("language", abbrev)
            self._update_lang_label()
        reply = resp.get("reply", "")
        self._append_text(self._sender_label(), reply)
        self._show_avatar_state("explaining")

    def _post_json(self, path: str, payload: dict) -> Optional[dict]:
        url = f"{self.api_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        if self.api_key:
            req.add_header("X-Jubie-Api-Key", self.api_key)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8")
            except Exception:
                detail = ""
            self._print_system_message(f"HTTP error {e.code}: {detail or e.reason}")
        except urllib.error.URLError as e:
            self._print_system_message(f"Connection error: {e.reason}. Is `jubie_api.py` running?")
        except Exception as e:  # pragma: no cover - generic fallback
            self._print_system_message(f"Unexpected error: {e}")
        return None

    def _sender_label(self) -> str:
        """Label for the current character in chat."""
        if self.mode == "katherine":
            return "[Katherine] "
        if self.mode == "komi":
            return "[Komi] "
        return f"[Jubei-Chan ({self.mode})] "

    def _send_message(self, message: str) -> None:
        payload = {
            "message": message,
            "personality": self.mode,
            "language": self.language,
        }
        resp = self._post_json("/chat", payload)
        if not resp:
            return
        # Handle character switch (Jubei - Switch - Katherine / Katherine - Switch - Jubei)
        if resp.get("character_switch"):
            self.mode = resp.get("mode", self.mode)
            self._update_mode_label()
            self._append_text(self._sender_label(), resp.get("reply", ""))
            self._show_avatar_state("explaining")
            return
        # Handle language change (user typed "Jubei - language - XX")
        if resp.get("language_change"):
            self.language = resp.get("language", self.language)
            self.language_var.set(self.language)
            self._update_lang_label()
        reply = resp.get("reply", "")
        mode = resp.get("mode", self.mode)
        self.mode = mode
        self._update_mode_label()
        self._append_text(self._sender_label(), reply)
        self._show_avatar_state("explaining")

    def _send_transform(self, message: str) -> None:
        payload = {
            "message": message,
            "previous_personality": self.mode,
        }
        resp = self._post_json("/chat", payload)
        if not resp:
            return
        # Transform responses carry the new mode explicitly.
        if resp.get("transform"):
            self.mode = resp.get("mode", self.mode)
            self._update_mode_label()
        reply = resp.get("reply", "")
        self._append_text(self._sender_label(), reply)
        self._show_avatar_state("explaining")

    def _update_mode_label(self) -> None:
        if self.mode == "katherine":
            display = "Katherine"
        elif self.mode == "komi":
            display = "Komi"
        else:
            display = self.mode
        self.mode_label.configure(text=f"Mode: {display}")

    def _on_close(self) -> None:
        """Show goodbye avatar, then close after a short delay."""
        self._show_avatar_state("goodbye")
        self._print_system_message("Jubei-Chan is saying goodbye. Closing in 10 seconds...")
        self.root.after(10000, self.root.destroy)


def main() -> None:
    root = tk.Tk()
    try:
        app = JubeiDesktopApp(root)
    except Exception as e:  # pragma: no cover - startup errors
        messagebox.showerror("Project Jubei", f"Failed to start Jubei desktop app:\n{e}")
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
