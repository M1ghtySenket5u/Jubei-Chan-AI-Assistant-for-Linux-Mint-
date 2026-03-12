import os
import webbrowser
from typing import Dict, Any

from flask import Flask, jsonify, request

from jubie_cli import (
    EASTER_EGG_TEMPEL_URL,
    EASTER_EGG_YOUNG_URL,
    EASTER_EGG_KINO_URL,
    TUX_ASCII_ART,
    NINJA_PERSONALITY,
    SCHOOLGIRL_PERSONALITY,
    KATHERINE_PERSONALITY,
    KOMI_PERSONALITY,
    Personality,
    SUPPORTED_LANGUAGES,
    use_llm_reply,
    offline_reply,
    load_env,
    get_console,
    _play_youtube_url,
    _stop_music,
    _open_krita,
    _open_vlc,
    _open_oneko,
    _slice_oneko,
    _open_gimp,
    _open_ani_cli,
    _slice_ani_cli,
    _open_hollywood,
    _slice_hollywood,
)


app = Flask(__name__)
load_env()
console = get_console()


def _select_personality(label: str) -> Personality:
    label = (label or "").strip().lower()
    if label in {"katherine"}:
        return KATHERINE_PERSONALITY
    if label in {"komi"}:
        return KOMI_PERSONALITY
    if label in {"schoolgirl", "highschool", "highschool_girl", "girl"}:
        return SCHOOLGIRL_PERSONALITY
    return NINJA_PERSONALITY


def _toggle_personality(label: str) -> Personality:
    current = _select_personality(label or "ninja")
    return SCHOOLGIRL_PERSONALITY if current is NINJA_PERSONALITY else NINJA_PERSONALITY


def _require_internal_key() -> bool:
    """
    Enforce the same JUBIE_API_KEY used by the CLI, but in a non-interactive way.
    - If JUBIE_API_KEY is not set, the API is open on localhost.
    - If it is set, clients must send it as either:
      - HTTP header: X-Jubie-Api-Key
      - JSON field:  jubie_api_key
    """
    env_key = os.getenv("JUBIE_API_KEY")
    if not env_key:
        return True

    incoming = (
        request.headers.get("X-Jubie-Api-Key")
        or (request.json or {}).get("jubie_api_key")
    )
    return bool(incoming and incoming == env_key)


@app.route("/health", methods=["GET"])
def health() -> Any:
    if not _require_internal_key():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat() -> Any:
    if not _require_internal_key():
        return jsonify({"error": "unauthorized"}), 401

    data: Dict[str, Any] = request.json or {}
    message = (data.get("message") or "").strip()
    personality_label = data.get("personality") or "ninja"
    previous_personality_label = data.get("previous_personality")
    language = (data.get("language") or "en").strip().lower()

    if not message:
        return jsonify({"error": "message is required"}), 400

    # Character switch: Jubei - Switch - Katherine
    if message.lower() == "jubei - switch - katherine":
        return jsonify(
            {
                "character_switch": True,
                "character": "katherine",
                "mode": "katherine",
                "reply": (
                    "*Character switch!* Katherine is now active. "
                    "Ask her anything—she's calm, thoughtful, and happy to help."
                ),
            }
        )

    # Character switch: Katherine - Switch - Jubei
    if message.lower() == "katherine - switch - jubei":
        return jsonify(
            {
                "character_switch": True,
                "character": "jubie",
                "mode": "schoolgirl",
                "reply": (
                    "*Character switch!* Jubei-Chan is back in Highschool Girl Mode. "
                    "Ask me anything!"
                ),
            }
        )

    # Character switch: Jubei - Switch - Komi
    if message.lower() == "jubei - switch - komi":
        return jsonify(
            {
                "character_switch": True,
                "character": "komi",
                "mode": "komi",
                "reply": (
                    "*Character switch!* Komi is now active. "
                    "Ask her anything—she's outgoing, friendly, and happy to help."
                ),
            }
        )

    # Character switch: Komi - Switch - Jubei
    if message.lower() == "komi - switch - jubei":
        return jsonify(
            {
                "character_switch": True,
                "character": "jubei",
                "mode": "schoolgirl",
                "reply": (
                    "*Character switch!* Jubei-Chan is back in Highschool Girl Mode. "
                    "Ask me anything!"
                ),
            }
        )

    # Character switch: Katherine - Switch - Komi
    if message.lower() == "katherine - switch - komi":
        return jsonify(
            {
                "character_switch": True,
                "character": "komi",
                "mode": "komi",
                "reply": (
                    "*Character switch!* Komi is now active. "
                    "Ask her anything—she's outgoing, friendly, and happy to help."
                ),
            }
        )

    # Character switch: Komi - Switch - Katherine
    if message.lower() == "komi - switch - katherine":
        return jsonify(
            {
                "character_switch": True,
                "character": "katherine",
                "mode": "katherine",
                "reply": (
                    "*Character switch!* Katherine is now active. "
                    "Ask her anything—she's calm, thoughtful, and happy to help."
                ),
            }
        )

    # Open Krita: "Open - Krita" (opens Krita; if not installed, character asks user to install)
    if message.lower() == "open - krita":
        personality = _select_personality(personality_label)
        ok, reply_text = _open_krita(console, personality)
        if ok:
            return jsonify({"open_krita": True, "reply": f"*{reply_text}*"})
        return jsonify({"open_krita": False, "reply": reply_text})

    # Open VLC: "Open - VLC" (opens VLC; installs if missing)
    if message.lower() == "open - vlc":
        personality = _select_personality(personality_label)
        ok, reply_text = _open_vlc(console, personality)
        if ok:
            return jsonify({"open_vlc": True, "reply": f"*{reply_text}*"})
        return jsonify({"open_vlc": False, "reply": reply_text})

    # Open Oneko: "Open - Oneko" (opens Oneko; installs if missing)
    if message.lower() == "open - oneko":
        personality = _select_personality(personality_label)
        ok, reply_text = _open_oneko(console, personality)
        if ok:
            return jsonify({"open_oneko": True, "reply": f"*{reply_text}*"})
        return jsonify({"open_oneko": False, "reply": reply_text})

    # Slice Oneko: "Slice - Oneko" (stops Oneko)
    if message.lower() == "slice - oneko":
        ok, reply_text = _slice_oneko()
        if ok:
            return jsonify({"slice_oneko": True, "reply": f"*{reply_text}*"})
        return jsonify({"slice_oneko": False, "reply": reply_text})

    # Open GIMP: "Open - GNU" (opens GNU Image Manipulation Program; installs if missing)
    if message.lower() == "open - gnu":
        personality = _select_personality(personality_label)
        ok, reply_text = _open_gimp(console, personality)
        if ok:
            return jsonify({"open_gimp": True, "reply": f"*{reply_text}*"})
        return jsonify({"open_gimp": False, "reply": reply_text})

    # Open ani-cli: "Open - Ani-cli" (opens ani-cli in a new terminal; requires pre-install)
    if message.lower() == "open - ani-cli":
        personality = _select_personality(personality_label)
        ok, reply_text = _open_ani_cli(console, personality)
        if ok:
            return jsonify({"open_ani_cli": True, "reply": f"*{reply_text}*"})
        return jsonify({"open_ani_cli": False, "reply": reply_text})

    # Slice ani-cli: "Slice - Ani-cli" (stops ani-cli)
    if message.lower() == "slice - ani-cli":
        ok, reply_text = _slice_ani_cli()
        if ok:
            return jsonify({"slice_ani_cli": True, "reply": f"*{reply_text}*"})
        return jsonify({"slice_ani_cli": False, "reply": reply_text})

    # Open Hollywood: "Open - Hollywood" (opens Hollywood in a new terminal; installs if missing)
    if message.lower() == "open - hollywood":
        personality = _select_personality(personality_label)
        ok, reply_text = _open_hollywood(console, personality)
        if ok:
            return jsonify({"open_hollywood": True, "reply": f"*{reply_text}*"})
        return jsonify({"open_hollywood": False, "reply": reply_text})

    # Slice Hollywood: "Slice - Hollywood" (stops Hollywood)
    if message.lower() == "slice - hollywood":
        ok, reply_text = _slice_hollywood()
        if ok:
            return jsonify({"slice_hollywood": True, "reply": f"*{reply_text}*"})
        return jsonify({"slice_hollywood": False, "reply": reply_text})

    # Support a stateless "transform" behaviour for API clients.
    if message.lower() == "jubei - transform":
        base_label = previous_personality_label or personality_label
        if base_label == "katherine":
            return jsonify(
                {
                    "reply": (
                        "Use 'Katherine - Switch - Jubei' first to return to Jubei-Chan."
                    ),
                    "mode": "katherine",
                }
            )
        if base_label == "komi":
            return jsonify(
                {
                    "reply": (
                        "Use 'Komi - Switch - Jubei' first to return to Jubei-Chan."
                    ),
                    "mode": "komi",
                }
            )
        new_personality = _toggle_personality(base_label)
        return jsonify(
            {
                "transform": True,
                "personality": new_personality.name,
                "mode": "schoolgirl"
                if new_personality is SCHOOLGIRL_PERSONALITY
                else "ninja",
                "reply": (
                    f"*Transformation!* Jubei-Chan is now in {new_personality.name}. "
                    "Send your next question with this personality."
                ),
            }
        )

    # Support "Jubei - language - XX" to change response language.
    lang_prefix = "jubei - language - "
    if message.lower().startswith(lang_prefix):
        abbrev = message[len(lang_prefix) :].strip().lower()
        if abbrev in SUPPORTED_LANGUAGES:
            new_lang = abbrev
            lang_name = SUPPORTED_LANGUAGES[abbrev]
            return jsonify(
                {
                    "language_change": True,
                    "language": new_lang,
                    "language_name": lang_name,
                    "reply": (
                        f"*Language changed!* Jubei-Chan will now respond in {lang_name}. "
                        "Send your next question and it will be answered in that language."
                    ),
                }
            )
        return jsonify(
            {
                "error": f"Unknown language abbreviation: {abbrev}. Supported: ja, es, de, ru, en"
            }
        ), 400

    # Easter eggs: Jubei, Katherine, or Komi can trigger any of these
    _easter_egg_prefixes = ("jubei - ", "katherine - ", "komi - ", "jubie - ")
    _msg_lower = message.lower()

    # Easter egg: CREATOR / Jubei - Creator (creator credits)
    if _msg_lower in (p + "creator" for p in _easter_egg_prefixes) or _msg_lower in {
        "creator",
        "who - is - your - creator",
    }:
        return jsonify(
            {
                "easter_egg": "creator",
                "reply": (
                    "The creator of Jubei-Chan AI is a University student from Lamar UNiversity named "
                    "Hector Flores or also known as Mighty Senketsu. He create Me (Jubei-Chan AI and friends) "
                    "to be your AI assistent buddy for Linux MInt. I'm here to teach you the world of Linux MInt!!!!"
                ),
            }
        )

    # Easter egg: Open Linux Mint website
    if _msg_lower in (p + "mint" for p in _easter_egg_prefixes):
        try:
            webbrowser.open("https://linuxmint.com/")
            reply_text = "Opening the Linux Mint website in your browser."
        except Exception:
            reply_text = "I tried but couldn't open the Linux Mint website."
        return jsonify({"easter_egg": "mint", "reply": reply_text})

    # Easter egg: Open Cinnamon themes website
    if _msg_lower in (p + "cinnamon" for p in _easter_egg_prefixes):
        try:
            webbrowser.open("https://www.cinnamon-look.org/s/Cinnamon/browse/")
            reply_text = "Opening the Cinnamon themes website in your browser."
        except Exception:
            reply_text = "I tried but couldn't open the Cinnamon themes website."
        return jsonify({"easter_egg": "cinnamon", "reply": reply_text})

    # Easter egg: Tempel (Temple OS theme)
    if _msg_lower in (p + "tempel" for p in _easter_egg_prefixes):
        if _play_youtube_url(EASTER_EGG_TEMPEL_URL, console):
            return jsonify(
                {
                    "easter_egg": "tempel",
                    "reply": "*Temple OS theme playing!* Type 'Jubei - Slice' to stop.",
                }
            )
        return jsonify({"easter_egg": "tempel", "reply": "Could not open audio."})

    # Easter egg: Tux (Linux mascot)
    if _msg_lower in (p + "tux" for p in _easter_egg_prefixes):
        return jsonify({"easter_egg": "tux", "reply": TUX_ASCII_ART.strip()})

    # Easter egg: Young Girl (song)
    if _msg_lower in (p + "young girl" for p in _easter_egg_prefixes) or _msg_lower in (
        p + "young" for p in _easter_egg_prefixes
    ):
        if _play_youtube_url(EASTER_EGG_YOUNG_URL, console):
            return jsonify(
                {
                    "easter_egg": "young_girl",
                    "reply": "*Young Girl playing!* Type 'Jubei - Slice' to stop.",
                }
            )
        return jsonify({"easter_egg": "young_girl", "reply": "Could not open audio."})

    # Easter egg: Kino - A pack of Cigarettes
    if _msg_lower in (p + "kino" for p in _easter_egg_prefixes):
        if _play_youtube_url(EASTER_EGG_KINO_URL, console):
            return jsonify(
                {
                    "easter_egg": "kino",
                    "reply": "*Kino - A pack of Cigarettes playing!* Type 'Jubei - Slice' to stop.",
                }
            )
        return jsonify({"easter_egg": "kino", "reply": "Could not open audio."})

    # Easter egg: Slice (stop music)
    if _msg_lower in (p + "slice" for p in _easter_egg_prefixes):
        if _stop_music():
            return jsonify({"easter_egg": "slice", "reply": "*Music stopped.*"})
        return jsonify({"easter_egg": "slice", "reply": "No music was playing."})

    personality = _select_personality(personality_label)

    used_llm = False
    reply = use_llm_reply(message, personality, console, language)
    if reply is None:
        reply = offline_reply(message, personality)
    else:
        used_llm = True

    mode = (
        "katherine"
        if personality is KATHERINE_PERSONALITY
        else "komi"
        if personality is KOMI_PERSONALITY
        else ("schoolgirl" if personality is SCHOOLGIRL_PERSONALITY else "ninja")
    )
    return jsonify(
        {
            "reply": reply,
            "personality": personality.name,
            "mode": mode,
            "language": language,
            "used_llm": used_llm,
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("JUBIE_API_PORT", "8000"))
    app.run(host="127.0.0.1", port=port)
