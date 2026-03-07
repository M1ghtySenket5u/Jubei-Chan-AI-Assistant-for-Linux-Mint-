import os
from typing import Dict, Any

from flask import Flask, jsonify, request

from jubie_cli import (
    EASTER_EGG_TEMPEL_URL,
    EASTER_EGG_YOUNG_URL,
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

    # Easter egg: Jubei - Tempel (Temple OS theme)
    if message.lower() == "jubei - tempel":
        if _play_youtube_url(EASTER_EGG_TEMPEL_URL, console):
            return jsonify(
                {
                    "easter_egg": "tempel",
                    "reply": "*Temple OS theme playing!* Type 'Jubei - Slice' to stop.",
                }
            )
        return jsonify({"easter_egg": "tempel", "reply": "Could not open audio."})

    # Easter egg: Jubei - Tux (Linux mascot)
    if message.lower() == "jubei - tux":
        return jsonify({"easter_egg": "tux", "reply": TUX_ASCII_ART.strip()})

    # Easter egg: Jubei - Young (Young song)
    if message.lower() == "jubei - young":
        if _play_youtube_url(EASTER_EGG_YOUNG_URL, console):
            return jsonify(
                {
                    "easter_egg": "young",
                    "reply": "*Young playing!* Type 'Jubei - Slice' to stop.",
                }
            )
        return jsonify({"easter_egg": "young", "reply": "Could not open audio."})

    # Easter egg: Jubei - Slice (stop music)
    if message.lower() == "jubei - slice":
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

