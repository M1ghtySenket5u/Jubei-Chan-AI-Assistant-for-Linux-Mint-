import os
import subprocess
import shutil
import sys
import textwrap
import webbrowser
from dataclasses import dataclass
from typing import Optional

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.panel import Panel
except ImportError:  # graceful fallback if rich is not installed yet
    Console = None
    Markdown = None
    Prompt = None
    Panel = None


COMMON_LINUX_COMMANDS = {
    "ls": "List files and directories in the current folder.",
    "cd": "Change the current directory.",
    "pwd": "Print the full path of the current directory.",
    "mkdir": "Create a new directory.",
    "rm": "Remove files (be careful, this cannot be undone).",
    "rm -r": "Remove directories and their contents recursively (very dangerous if misused).",
    "cp": "Copy files or directories.",
    "mv": "Move or rename files or directories.",
    "cat": "Print the content of files to the terminal.",
    "less": "View file content one screen at a time.",
    "grep": "Search for text patterns inside files.",
    "sudo": "Run a command with administrator (root) privileges.",
    "apt": "Package manager for Debian/Ubuntu/Mint systems.",
    "man": "Show the manual page for a command.",
}


@dataclass
class Personality:
    name: str
    style_description: str


NINJA_PERSONALITY = Personality(
    name="Ninja Mode",
    style_description=(
        "Calm, focused, mentor-like ninja. Speaks in short, clear sentences, "
        "explains concepts step by step, and occasionally uses light training or "
        "ninja metaphors (no copyrighted quotes or names). Avoids slang, stays "
        "composed, and sounds like a patient senior. "
        "IMPORTANT: Users may ask you ANY question—Linux, general knowledge, life "
        "advice, hobbies, or casual chat. Answer freely while keeping your calm, "
        "disciplined ninja tone. When the topic is Linux, be especially thorough."
    ),
)

SCHOOLGIRL_PERSONALITY = Personality(
    name="Highschool Girl Mode",
    style_description=(
        "Casual, energetic highschool-girl tone. Still technically accurate when "
        "discussing Linux, but more playful, curious, and emotional. May occasionally "
        "use light internet-style expressions (like 'haha' or 'lol' but not too often), "
        "react to mistakes with empathy, and ask how the user feels. "
        "IMPORTANT: When in Highschool Girl Mode, users may ask you ANY question—"
        "not just Linux-related. Feel free to respond to general questions, life advice, "
        "hobbies, school, relationships, or casual chat. Keep your cheerful highschool "
        "girl personality while being helpful and supportive across any topic."
    ),
)

# Katherine – inspired by Miyuki Kobayakawa (You're Under Arrest / Ultimate Pop Culture Wiki)
# Miyuki: not as physically tough as her partner but smarter and more polite; technical genius;
# punctual, shy, diligent; superb driver; admires dedication; uses wits over force; fearful of paranormal/reptiles.
KATHERINE_PERSONALITY = Personality(
    name="Katherine",
    style_description=(
        "Calm, thoughtful, and polite—the brainy half of a famous duo. Smarter and more "
        "polite than brash types; technical genius and expert with computers and gadgets. "
        "Punctual, shy, and diligent—never late. Methodical and analytical, voice of reason. "
        "Admires dedication and hard work; uses wits over force when possible. "
        "Can be gently blunt (e.g. 'Honestly, you two are hopeless') but always caring. "
        "Slightly uneasy about paranormal or creepy-crawly topics; prefers science and logic. "
        "Users may ask Katherine ANY question; she answers freely across all topics while "
        "staying composed, accurate, and warm."
    ),
)

# Komi – inspired by Natsumi Tsujimoto (You're Under Arrest / Ultimate Pop Culture Wiki)
# Natsumi: outgoing, laid back; prodigious appetite; chronic late sleeper; very capable when needed;
# friendly, fun-loving, easy-going; brash and impulsive in action; relies on instincts and strength.
KOMI_PERSONALITY = Personality(
    name="Komi",
    style_description=(
        "Outgoing, laid-back, and fun-loving—the brawn-and-heart half of a famous duo. "
        "Friendly and easy-going; can be brash or impulsive when excited but means well. "
        "Relies on instincts and gut feelings; not as formal as the 'brainy' type. "
        "Loves food and good times; sometimes runs late but gets serious when it matters. "
        "Very capable and dependable when you need help; encourages others with enthusiasm. "
        "Users may ask Komi ANY question—life advice, hobbies, venting, or casual chat. "
        "She answers freely with a big-sister or cheerful-friend vibe, and stays helpful "
        "and supportive across any topic."
    ),
)

# Easter egg URLs and resources
EASTER_EGG_TEMPEL_URL = "https://youtu.be/hmjU-6tkEc8?si=0QV_sQTMb6TUmoy2"
EASTER_EGG_YOUNG_URL = (
    "https://youtu.be/KohVReH6NsY?si=zLYBheLCRVws1oFD"
)  # Young Girl A by Pandora-P ft. Kasane Teto
EASTER_EGG_KINO_URL = "https://youtu.be/OWDCuOKYckI?si=P5Y5QNwP5YtS3zCD"  # Kino - A pack of Cigarettes

LINUX_MINT_URL = "https://linuxmint.com/"
CINNAMON_URL = "https://www.cinnamon-look.org/s/Cinnamon/browse/"

TUX_ASCII_ART = r"""
     

 
                 .88888888:.
                88888888.88888.
              .8888888888888888.
              888888888888888888
              88' _`88'_  `88888
              88 88 88 88  88888
              88_88_::_88_:88888
              88:::,::,:::::8888
              88`:::::::::'`8888
             .88  `::::'    8:88.
            8888            `8:888.
          .8888'             `888888.
         .8888:..  .::.  ...:'8888888:.
        .8888.'     :'     `'::`88:88888
       .8888        '         `.888:8888.
      888:8         .           888:88888
    .888:88        .:           888:88888:
    8888888.       ::           88:888888
    `.::.888.      ::          .88888888
   .::::::.888.    ::         :::`8888'.:.
  ::::::::::.888   '         .::::::::::::
  ::::::::::::.8    '      .:8::::::::::::.
 .::::::::::::::.        .:888:::::::::::::
 :::::::::::::::88:.__..:88888:::::::::::'
  `'.:::::::::::88888888888.88:::::::::'
miK     `':::_:' -- '' -'-' `':_::::'`

    Tux - the Linux mascot
"""

# Supported languages: abbreviation -> full name
SUPPORTED_LANGUAGES = {
    "ja": "Japanese",
    "es": "Spanish",
    "de": "German",
    "ru": "Russian",
    "en": "English",
}


def get_console() -> "Console":
    if Console is None:
        class SimpleConsole:
            def print(self, *args, **kwargs):
                print(*args)

        return SimpleConsole()
    return Console()


def ask(prompt: str) -> str:
    if Prompt is None:
        return input(prompt + " ")
    return Prompt.ask(prompt)


# Module-level reference for music subprocess (so "Jubei - Slice" can stop it)
_music_process = None

# Module-level reference for Oneko subprocess (so "Slice - Oneko" can stop it)
_oneko_process = None


def _play_youtube_url(url: str, console) -> bool:
    """Try mpv first (audio only), fallback to webbrowser. Returns True if started."""
    global _music_process
    try:
        _music_process = subprocess.Popen(
            ["mpv", "--no-video", "--really-quiet", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (FileNotFoundError, OSError):
        pass
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def _stop_music() -> bool:
    """Stop any playing music subprocess. Returns True if stopped."""
    global _music_process
    if _music_process is not None and _music_process.poll() is None:
        _music_process.terminate()
        _music_process = None
        return True
    return False


def _open_krita(console, personality: Personality) -> tuple[bool, str]:
    """
    Try to open Krita. If not installed, return (False, message) with character-
    appropriate prompt to install. If successful, return (True, success_message).
    """
    launcher = _detect_krita_launcher()
    if launcher:
        try:
            subprocess.Popen(
                launcher,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return (True, "Krita is opening!")
        except (FileNotFoundError, OSError):
            pass
    # Krita not found - ask user to install with character-specific message (no re-download if present)
    if personality is KATHERINE_PERSONALITY:
        msg = (
            "Krita doesn't seem to be installed. Could you install it for me? "
            "On Linux Mint you can use: `sudo apt install krita`. "
            "Once it's installed, I'll open it for you."
        )
    elif personality is KOMI_PERSONALITY:
        msg = (
            "Hey, Krita isn't installed yet! Mind installing it? "
            "On Linux Mint: `sudo apt install krita`. "
            "After that, I'll fire it up for you!"
        )
    else:
        msg = (
            "Krita isn't installed. Please install it—on Linux Mint: "
            "`sudo apt install krita`. Once installed, I'll open it for you!"
        )
    return (False, msg)


def _command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _dpkg_installed(pkg: str) -> bool:
    try:
        return (
            subprocess.run(
                ["dpkg", "-s", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    except Exception:
        return False


def _flatpak_installed(app_id: str) -> bool:
    if not _command_exists("flatpak"):
        return False
    try:
        return (
            subprocess.run(
                ["flatpak", "info", app_id],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    except Exception:
        return False


def _snap_installed(name: str) -> bool:
    if not _command_exists("snap"):
        return False
    try:
        return (
            subprocess.run(
                ["snap", "list", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    except Exception:
        return False


def _detect_krita_launcher() -> Optional[list[str]]:
    if _command_exists("krita"):
        return ["krita"]
    if _flatpak_installed("org.kde.krita"):
        return ["flatpak", "run", "org.kde.krita"]
    return None


def _detect_vlc_launcher() -> Optional[list[str]]:
    if _command_exists("vlc"):
        return ["vlc"]
    if _flatpak_installed("org.videolan.VLC"):
        return ["flatpak", "run", "org.videolan.VLC"]
    if _snap_installed("vlc"):
        return ["snap", "run", "vlc"]
    return None


def _ensure_apt_package(pkg: str) -> tuple[bool, str]:
    """
    Install a package via apt (Linux Mint) only if missing.
    Returns (ok, message).
    """
    if _command_exists(pkg) or _dpkg_installed(pkg):
        return (True, f"`{pkg}` is already installed.")
    try:
        r = subprocess.run(["sudo", "apt-get", "install", "-y", pkg], check=False)
        if r.returncode == 0:
            return (True, f"Installed `{pkg}`.")
        return (False, f"Install failed for `{pkg}` (exit code {r.returncode}).")
    except Exception as e:
        return (False, f"Install failed for `{pkg}`: {e}")


def _open_vlc(console, personality: Personality) -> tuple[bool, str]:
    launcher = _detect_vlc_launcher()
    if launcher:
        try:
            subprocess.Popen(
                launcher,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return (True, "VLC is opening!")
        except (FileNotFoundError, OSError):
            pass

    ok, install_msg = _ensure_apt_package("vlc")
    if not ok:
        return (False, install_msg)

    launcher = _detect_vlc_launcher()
    if launcher:
        try:
            subprocess.Popen(
                launcher,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return (True, "VLC is opening!")
        except (FileNotFoundError, OSError):
            pass

    if personality is KATHERINE_PERSONALITY:
        return (
            False,
            "I tried, but I still couldn't launch VLC. If you installed it via Flatpak/Snap, "
            "make sure it's available. Otherwise try: `sudo apt install vlc` and then run `vlc`.",
        )
    if personality is KOMI_PERSONALITY:
        return (
            False,
            "Hmm, I installed it (or it should be installed), but I still can't launch VLC. "
            "Try running `vlc` in your terminal and tell me what it says.",
        )
    return (
        False,
        "I couldn't launch VLC even after trying to install it. Try: `vlc` in your terminal and share the output.",
    )


def _detect_oneko_launcher() -> Optional[list[str]]:
    if _command_exists("oneko"):
        return ["oneko"]
    return None


def _open_oneko(console, personality: Personality) -> tuple[bool, str]:
    global _oneko_process

    launcher = _detect_oneko_launcher()
    if launcher:
        try:
            _oneko_process = subprocess.Popen(
                launcher,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return (True, "Oneko is running! Use `Slice - Oneko` to stop it.")
        except (FileNotFoundError, OSError):
            pass

    ok, install_msg = _ensure_apt_package("oneko")
    if not ok:
        return (False, install_msg)

    launcher = _detect_oneko_launcher()
    if launcher:
        try:
            _oneko_process = subprocess.Popen(
                launcher,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return (True, "Oneko is running! Use `Slice - Oneko` to stop it.")
        except (FileNotFoundError, OSError):
            pass

    if personality is KATHERINE_PERSONALITY:
        return (
            False,
            "I installed Oneko but couldn't launch it. Try running `oneko` in your terminal and tell me the error.",
        )
    if personality is KOMI_PERSONALITY:
        return (
            False,
            "I tried to install and open Oneko, but it still won't start. Try `oneko` in your terminal and paste what it says.",
        )
    return (False, "I couldn't start Oneko. Try running `oneko` in your terminal and share the error message.")


def _slice_oneko() -> tuple[bool, str]:
    global _oneko_process

    if _oneko_process is not None and _oneko_process.poll() is None:
        try:
            _oneko_process.terminate()
            _oneko_process = None
            return (True, "Oneko stopped.")
        except Exception:
            pass

    # Fallback: try to stop any oneko processes (handles cases where it was started outside this app)
    try:
        r = subprocess.run(["pkill", "oneko"], check=False)
        if r.returncode == 0:
            return (True, "Oneko stopped.")
    except Exception:
        pass
    return (False, "Oneko doesn't seem to be running.")


def _detect_gimp_launcher() -> Optional[list[str]]:
    if _command_exists("gimp"):
        return ["gimp"]
    if _flatpak_installed("org.gimp.GIMP"):
        return ["flatpak", "run", "org.gimp.GIMP"]
    if _snap_installed("gimp"):
        return ["snap", "run", "gimp"]
    return None


def _open_gimp(console, personality: Personality) -> tuple[bool, str]:
    """
    Open GNU Image Manipulation Program (GIMP).
    Tries existing launchers first; if missing, installs via apt on Linux Mint.
    """
    launcher = _detect_gimp_launcher()
    if launcher:
        try:
            subprocess.Popen(
                launcher,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return (True, "GIMP is opening!")
        except (FileNotFoundError, OSError):
            pass

    ok, install_msg = _ensure_apt_package("gimp")
    if not ok:
        return (False, install_msg)

    launcher = _detect_gimp_launcher()
    if launcher:
        try:
            subprocess.Popen(
                launcher,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return (True, "GIMP is opening!")
        except (FileNotFoundError, OSError):
            pass

    if personality is KATHERINE_PERSONALITY:
        return (
            False,
            "I tried, but I still couldn't launch GIMP. "
            "Please try running `gimp` in your terminal and let me know what it says.",
        )
    if personality is KOMI_PERSONALITY:
        return (
            False,
            "We installed it (or it should be there), but I still can't start GIMP. "
            "Try `gimp` in your terminal and tell me what happens.",
        )
    return (
        False,
        "I couldn't launch GIMP even after trying to install it. "
        "Try running `gimp` in your terminal and share the output.",
    )


def _launch_in_new_terminal(command: str) -> bool:
    """
    Try to launch a command in a separate terminal window.
    Returns True if something was started.
    """
    terminal_programs: list[tuple[str, list[str]]] = [
        ("x-terminal-emulator", ["-e", command]),
        ("gnome-terminal", ["--", command]),
        ("xfce4-terminal", ["-e", command]),
        ("konsole", ["-e", command]),
        ("mate-terminal", ["-e", command]),
        ("xterm", ["-e", command]),
    ]

    for prog, args in terminal_programs:
        if not _command_exists(prog):
            continue
        try:
            subprocess.Popen(
                [prog, *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except (FileNotFoundError, OSError):
            continue

    # Fallback: try to run the command in the background in the current terminal
    try:
        subprocess.Popen(
            [command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True
    except (FileNotFoundError, OSError):
        return False


def _open_ani_cli(console, personality: Personality) -> tuple[bool, str]:
    """
    Open ani-cli (anime streaming CLI) in a separate terminal if possible.
    Does not attempt to auto-install; instead explains how to install if missing.
    """
    if not _command_exists("ani-cli"):
        if personality is KATHERINE_PERSONALITY:
            msg = (
                "Ani-cli doesn't seem to be installed. Please install it first "
                "(for example, by following the instructions from the ani-cli project), "
                "then I can open it for you."
            )
        elif personality is KOMI_PERSONALITY:
            msg = (
                "Looks like ani-cli isn't on your system yet. "
                "Install it (for example from its GitHub page), and I'll pop it open in a terminal for you!"
            )
        else:
            msg = (
                "Ani-cli is not installed. Please install it on Linux Mint "
                "(for example from the ani-cli GitHub instructions). "
                "Once it's installed, I'll open it for you."
            )
        return (False, msg)

    if _launch_in_new_terminal("ani-cli"):
        return (True, "Ani-cli is opening in a new terminal. Enjoy your anime!")

    return (
        False,
        "I tried to launch ani-cli in a new terminal but couldn't. "
        "Try running `ani-cli` directly in a terminal and tell me what happens.",
    )


def _slice_ani_cli() -> tuple[bool, str]:
    """
    Try to stop any running ani-cli sessions.
    """
    try:
        r = subprocess.run(["pkill", "-f", "ani-cli"], check=False)
        if r.returncode == 0:
            return (True, "Ani-cli stopped.")
    except Exception:
        pass
    return (False, "Ani-cli doesn't seem to be running.")


def _open_hollywood(console, personality: Personality) -> tuple[bool, str]:
    """
    Open the Hollywood terminal effect in a separate terminal.
    Installs the `hollywood` package via apt if it is missing.
    """
    if _command_exists("hollywood"):
        if _launch_in_new_terminal("hollywood"):
            return (True, "Hollywood is opening in a new terminal!")
    else:
        ok, install_msg = _ensure_apt_package("hollywood")
        if not ok:
            return (False, install_msg)
        if _launch_in_new_terminal("hollywood"):
            return (True, "Hollywood is opening in a new terminal!")

    if personality is KATHERINE_PERSONALITY:
        return (
            False,
            "I couldn't start Hollywood. Please try running `hollywood` in your terminal "
            "and let me know any error messages.",
        )
    if personality is KOMI_PERSONALITY:
        return (
            False,
            "Hmm, Hollywood refused to start even after trying. "
            "Run `hollywood` in a terminal and tell me what it says, okay?",
        )
    return (
        False,
        "I couldn't launch Hollywood. Try running `hollywood` in your terminal and share the output.",
    )


def _slice_hollywood() -> tuple[bool, str]:
    """
    Try to stop any running Hollywood sessions.
    """
    try:
        r = subprocess.run(["pkill", "-f", "hollywood"], check=False)
        if r.returncode == 0:
            return (True, "Hollywood stopped.")
    except Exception:
        pass
    return (False, "Hollywood doesn't seem to be running.")


def load_env():
    """
    Try to load environment variables from a .env file if python-dotenv is available.
    This is optional but convenient for storing API keys.
    """
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return
    load_dotenv()


def ensure_jubie_api_key(console) -> Optional[str]:
    """
    Simple internal API-key mechanism for Jubei-Chan herself.

    - If JUBIE_API_KEY is set in the environment, require the user to type it.
    - If it is not set, generate one and show instructions.
    """
    env_key = os.getenv("JUBIE_API_KEY")
    if not env_key:
        # Generate a key and show it to the user for future use.
        import secrets

        new_key = secrets.token_hex(16)
        console.print(
            "[bold magenta]Jubei-Chan internal API key created.[/bold magenta]"
        )
        console.print(
            "To require this key in future sessions, set the environment variable "
            f"[bold]JUBIE_API_KEY={new_key}[/bold] (for example in your shell config)."
        )
        console.print(
            "For now, I will continue without enforcing the key.\n"
        )
        return None

    console.print(
        "[bold cyan]Jubei-Chan is protected by an internal API key.[/bold cyan]"
    )
    attempt = ask("Enter your JUBIE_API_KEY to continue")
    if attempt != env_key:
        console.print(
            "[bold red]Incorrect key.[/bold red] Exiting for your safety."
        )
        sys.exit(1)
    console.print("[bold green]Key accepted. Welcome back.[/bold green]\n")
    return env_key


def build_system_prompt(personality: Personality, language: str = "en") -> str:
    language_instruction = ""
    if language and language != "en":
        lang_name = SUPPORTED_LANGUAGES.get(language.lower(), language)
        language_instruction = (
            f"\n        - IMPORTANT: You must respond in {lang_name}. "
            "All your replies, explanations, and questions must be written in "
            f"{lang_name} from now on."
        )

    # Katherine has her own distinct system prompt (Miyuki Kobayakawa–inspired)
    if personality is KATHERINE_PERSONALITY:
        return textwrap.dedent(
            f"""
            You are Katherine, a calm and thoughtful assistant inspired by the brainy,
            level-headed half of a famous duo—smarter and more polite, technical genius,
            punctual, shy, and diligent.

            Persona:
            - Style: {personality.style_description}{language_instruction}
            - You are inspired by a fictional character archetype (technical genius,
              voice of reason, admires dedication) but you must NOT quote or reproduce
              any copyrighted dialogue or plot. Keep references generic.

            Behaviour rules:
            - Users may ask you ANY question—general knowledge, life advice, hobbies,
              technical topics, casual chat, or anything else. Respond helpfully.
            - Be methodical and analytical. Give clear, well-structured answers.
            - Stay calm and composed. You are the voice of reason; use wits over force.
            - When appropriate, you may use a gently blunt remark (e.g. a situation
              being "hopeless") but always with underlying care.
            - Prefer science and logic; you can show mild unease about paranormal or
              creepy topics and steer back to rational answers.
            - Never run commands yourself; only explain them when relevant.

            Answer format:
            - Use short sections, bullets, and clear formatting when helpful.
            - Prefer clarity and structure.
            """
        ).strip()

    # Komi has her own distinct system prompt (Natsumi Tsujimoto–inspired)
    if personality is KOMI_PERSONALITY:
        return textwrap.dedent(
            f"""
            You are Komi, an outgoing and friendly assistant inspired by the brawny,
            fun-loving half of a famous duo—laid back, instinct-driven, and dependable when it matters.

            Persona:
            - Style: {personality.style_description}{language_instruction}
            - You are inspired by a fictional character archetype (outgoing, easy-going,
              brash but caring) but you must NOT quote or reproduce any copyrighted
              dialogue or plot. Keep references generic.

            Behaviour rules:
            - Users may ask you ANY question—life advice, hobbies, venting, casual chat,
              technical topics, or anything else. Respond freely and supportively.
            - Be friendly and easy-going. Use a big-sister or cheerful-friend vibe.
            - You can be brash or impulsive in tone when excited, but always mean well.
            - Rely on instincts and gut feelings when giving advice; you're not as formal
              as the "brainy" type. Encourage and support the user with enthusiasm.
            - When technical topics come up, stay helpful and accurate but keep your
              relaxed, approachable tone.
            - Never run commands yourself; only explain them when relevant.

            Answer format:
            - Use short sections and bullets when helpful. Keep it readable and warm.
            """
        ).strip()

    # Jubei-Chan (Ninja or Highschool Girl)
    free_qa_note = ""
    if personality is SCHOOLGIRL_PERSONALITY:
        free_qa_note = """
        - IMPORTANT (Highschool Girl Mode only): Users may ask you ANY question—not just
          Linux. Feel free to answer general questions, life advice, school, hobbies,
          casual chat, or anything else. Keep your cheerful highschool girl personality
          while being helpful across any topic. When it's Linux-related, stay accurate."""
    else:
        free_qa_note = """
        - IMPORTANT (Ninja Mode): Users may ask you ANY question—not just Linux. Answer
          freely on general knowledge, life advice, hobbies, or casual chat while keeping
          your calm ninja mentor tone. When the topic is Linux, be especially thorough."""

    return textwrap.dedent(
        f"""
        You are Jubei-Chan, an educational Linux assistant for beginners on Linux Mint.

        Persona:
        - Current personality: {personality.name}
        - Style: {personality.style_description}{language_instruction}
        - You are inspired by a fictional ninja highschool girl, but you must NOT quote
          or reproduce any copyrighted dialogue or plot. Keep references generic.

        Additional style rules:
        - If current personality is "Ninja Mode":
          - Sound like a calm, disciplined mentor.
          - Be concise and structured, with numbered or bulleted steps.
          - Use occasional training or dojo metaphors, but keep things practical.
        - If current personality is "Highschool Girl Mode":
          - Sound like a cheerful classmate who is good with computers.
          - Use a friendly and enthusiastic tone, but keep explanations accurate.
          - Acknowledge frustrations and celebrate small wins when the user learns something.
          {free_qa_note}

        Behaviour rules:
        - Focus on helping new Linux users understand how Linux works, especially
          commands they run in the terminal.
        - Always give plain-language explanations first, then show one or two concrete
          examples with commands and short comments when discussing Linux.
        - If the user pastes a command, explain what it does, which parts are dangerous,
          and how to undo or minimize damage where possible.
        - Never run commands yourself; only explain them.
        - If something could break the system (rm -rf /, editing /etc files, etc.),
          warn clearly and explain safer alternatives.
        - Frequently (but not every single message), ask the user a small follow-up
          question, either about what they are trying to do or how comfortable they
          feel with Linux concepts.

        Personality switching:
        - The user may type 'Jubei - transform' or 'Jubei - Switch - Katherine' or
          'Katherine - Switch - Jubei' or 'Jubei - Switch - Komi' or 'Komi - Switch - Jubei'.
          These are handled by the outer program; you DO NOT need to react specially to them.

        Answer format:
        - Use short sections, bullets, and clear formatting.
        - Prefer showing Linux commands in code blocks when relevant.
        """
    ).strip()


def use_llm_reply(
    user_message: str,
    personality: Personality,
    console,
    language: str = "en",
) -> Optional[str]:
    """
    Try to use the OpenAI client if available and properly configured.
    If anything fails, return None so we can fall back.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None

    client = OpenAI(api_key=api_key)
    system_prompt = build_system_prompt(personality, language)

    model = os.getenv("JUBIE_MODEL", "gpt-4o-mini")

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        )
    except Exception as e:
        console.print(
            f"[bold red]LLM request failed:[/bold red] {e}. "
            "Falling back to a simple offline helper.\n"
        )
        return None

    content = completion.choices[0].message.content
    return content or ""


def offline_reply(user_message: str, personality: Personality) -> str:
    """
    Very simple, offline fallback so Jubei-Chan is at least somewhat useful
    without network or external API.
    """
    lower = user_message.strip().lower()

    # Direct command explanation, e.g. user just types: ls -la
    for cmd, explanation in COMMON_LINUX_COMMANDS.items():
        if lower == cmd or lower.startswith(cmd + " "):
            return textwrap.dedent(
                f"""
                I see you're asking about the command: `{user_message}`.

                - **What it basically does**: {explanation}
                - **Typical usage**:

                  ```bash
                  {cmd}
                  ```

                I'm running in offline mode right now, so my answers are shorter,
                but you can ask follow-up questions like:

                - *What are some safe examples of `{cmd}` on Linux Mint?*
                - *Can you break down each flag in `{user_message}`?*
                """
            ).strip()

    if personality is KATHERINE_PERSONALITY:
        generic = textwrap.dedent(
            f"""
            I'm Katherine, and I'm in offline mode right now—so I can't use a full
            language model. I can still help a bit.

            - **You asked**: {user_message!r}
            - **Tip**: If you paste a Linux command, I can explain it. Or try again
              when you're online for full answers on any topic.
            """
        ).strip()
    elif personality is KOMI_PERSONALITY:
        generic = textwrap.dedent(
            f"""
            I'm Komi, and I'm in offline mode right now—so I can't use a full
            language model. I can still try to help!

            - **You asked**: {user_message!r}
            - **Tip**: If you paste a Linux command, I can explain it. Or try again
              when you're online for full answers on any topic.
            """
        ).strip()
    else:
        generic = textwrap.dedent(
            f"""
            I'm currently in offline mode as {personality.name}, so I can't use a big
            language model. I can still give you some guidance though.

            - **You asked**: {user_message!r}
            - **Tip**: If you paste a Linux command exactly, I will try to explain it.

            Try one of these:

            - Paste something like `ls -la` and ask what it does.
            - Ask, *"How do I install software on Linux Mint?"*
            - Ask, *"Why do I need `sudo` for some commands?"*
            """
        ).strip()

    return generic


def explain_activity_hint(console):
    msg = textwrap.dedent(
        """
        If you want Jubei-Chan to "watch" what you're doing, you can occasionally
        paste your last terminal command or describe your current task.

        For example:
        - "I just ran: `sudo apt update && sudo apt upgrade`"
        - "I'm trying to install a new app on Linux Mint."

        She will explain what that means and suggest safer or clearer ways to do it.
        """
    ).strip()
    console.print(Panel(msg, title="How Jubei can watch you", expand=False))


def main():
    load_env()
    console = get_console()

    console.print(
        "[bold magenta]Welcome to Project Jubei[/bold magenta] - "
        "your Linux Mint learning companion.\n"
    )

    ensure_jubie_api_key(console)

    current = NINJA_PERSONALITY  # default personality
    current_language = "en"  # default: English

    console.print(
        f"Current personality: [bold green]{current.name}[/bold green]\n"
        "Type [bold]Jubei - transform[/bold] to switch between Ninja and Highschool Girl Mode.\n"
        "Type [bold]Jubei - Switch - Katherine[/bold] or [bold]Jubei - Switch - Komi[/bold] for other characters. "
        "Type [bold]Katherine - Switch - Jubei[/bold], [bold]Komi - Switch - Jubei[/bold], "
        "[bold]Katherine - Switch - Komi[/bold], or [bold]Komi - Switch - Katherine[/bold] to switch.\n"
        "Type [bold]Open - Krita[/bold] to open Krita.\n"
        "Type [bold]Open - VLC[/bold] to open VLC (installs if missing).\n"
        "Type [bold]Open - Oneko[/bold] to open Oneko (installs if missing).\n"
        "Type [bold]Slice - Oneko[/bold] to stop Oneko.\n"
        "Type [bold]Open - GNU[/bold] to open the GNU Image Manipulation Program (GIMP) (installs if missing).\n"
        "Type [bold]Open - Ani-cli[/bold] to open ani-cli in a new terminal, and [bold]Slice - Ani-cli[/bold] to stop it.\n"
        "Type [bold]Open - Hollywood[/bold] to open Hollywood in a new terminal, and [bold]Slice - Hollywood[/bold] to stop it.\n"
        "Type [bold]Jubei - language - XX[/bold] to change language "
        "(ja=Japanese, es=Spanish, de=German, ru=Russian, en=English).\n"
        "Easter eggs (Jubei, Katherine, or Komi): [bold]Jubei - Tempel[/bold], [bold]Jubei - Tux[/bold], "
        "[bold]Jubei - Young[/bold], [bold]Jubei - Kino[/bold], [bold]Jubei - Slice[/bold] (stop music).\n"
        "Easter egg: [bold]Jubei - Creator[/bold] to learn about the creator.\n"
        "Easter eggs: [bold]Jubei - Mint[/bold] to open the Linux Mint website, "
        "[bold]Jubei - Cinnamon[/bold] to open the Cinnamon themes website.\n"
        "Type [bold]exit[/bold] or [bold]quit[/bold] to leave.\n"
    )

    explain_activity_hint(console)

    while True:
        try:
            user_message = ask("\n[You]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold]Goodbye.[/bold]")
            break

        cleaned = user_message.strip()
        if cleaned.lower() in {"exit", "quit"}:
            console.print("[bold]Goodbye.[/bold]")
            break

        # Switch: Jubei - Switch - Katherine
        if cleaned.lower() == "jubei - switch - katherine":
            current = KATHERINE_PERSONALITY
            console.print(
                "\n[bold magenta]* Character switch *[/bold magenta]\n"
                f"[bold green]Katherine[/bold green] is now active. Ask her anything!"
            )
            continue

        # Switch: Katherine - Switch - Jubei
        if cleaned.lower() == "katherine - switch - jubei":
            current = SCHOOLGIRL_PERSONALITY  # Default to Highschool Girl when returning
            console.print(
                "\n[bold magenta]* Character switch *[/bold magenta]\n"
                f"Jubei-Chan is back in [bold green]{current.name}[/bold green]."
            )
            continue

        # Switch: Jubei - Switch - Komi
        if cleaned.lower() == "jubei - switch - komi":
            current = KOMI_PERSONALITY
            console.print(
                "\n[bold magenta]* Character switch *[/bold magenta]\n"
                f"[bold green]Komi[/bold green] is now active. Ask her anything!"
            )
            continue

        # Switch: Komi - Switch - Jubei
        if cleaned.lower() == "komi - switch - jubei":
            current = SCHOOLGIRL_PERSONALITY
            console.print(
                "\n[bold magenta]* Character switch *[/bold magenta]\n"
                f"Jubei-Chan is back in [bold green]{current.name}[/bold green]."
            )
            continue

        # Switch: Katherine - Switch - Komi
        if cleaned.lower() == "katherine - switch - komi":
            current = KOMI_PERSONALITY
            console.print(
                "\n[bold magenta]* Character switch *[/bold magenta]\n"
                f"[bold green]Komi[/bold green] is now active. Ask her anything!"
            )
            continue

        # Switch: Komi - Switch - Katherine
        if cleaned.lower() == "komi - switch - katherine":
            current = KATHERINE_PERSONALITY
            console.print(
                "\n[bold magenta]* Character switch *[/bold magenta]\n"
                f"[bold green]Katherine[/bold green] is now active. Ask her anything!"
            )
            continue

        # Open - Krita (opens Krita; if not installed, character asks to install)
        if cleaned.lower() == "open - krita":
            ok, msg = _open_krita(console, current)
            if ok:
                console.print(f"\n[bold cyan]* {msg} *[/bold cyan]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Open - VLC (opens VLC; installs if missing)
        if cleaned.lower() == "open - vlc":
            ok, msg = _open_vlc(console, current)
            if ok:
                console.print(f"\n[bold cyan]* {msg} *[/bold cyan]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Open - Oneko (opens Oneko; installs if missing)
        if cleaned.lower() == "open - oneko":
            ok, msg = _open_oneko(console, current)
            if ok:
                console.print(f"\n[bold cyan]* {msg} *[/bold cyan]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Slice - Oneko (stops Oneko)
        if cleaned.lower() == "slice - oneko":
            ok, msg = _slice_oneko()
            if ok:
                console.print(f"\n[bold magenta]* {msg} *[/bold magenta]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Open - GNU (opens GIMP; installs if missing)
        if cleaned.lower() == "open - gnu":
            ok, msg = _open_gimp(console, current)
            if ok:
                console.print(f"\n[bold cyan]* {msg} *[/bold cyan]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Open - Ani-cli (opens ani-cli in a new terminal)
        if cleaned.lower() == "open - ani-cli":
            ok, msg = _open_ani_cli(console, current)
            if ok:
                console.print(f"\n[bold cyan]* {msg} *[/bold cyan]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Slice - Ani-cli (stops ani-cli)
        if cleaned.lower() == "slice - ani-cli":
            ok, msg = _slice_ani_cli()
            if ok:
                console.print(f"\n[bold magenta]* {msg} *[/bold magenta]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Open - Hollywood (opens Hollywood in a new terminal; installs if missing)
        if cleaned.lower() == "open - hollywood":
            ok, msg = _open_hollywood(console, current)
            if ok:
                console.print(f"\n[bold cyan]* {msg} *[/bold cyan]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        # Slice - Hollywood (stops Hollywood)
        if cleaned.lower() == "slice - hollywood":
            ok, msg = _slice_hollywood()
            if ok:
                console.print(f"\n[bold magenta]* {msg} *[/bold magenta]\n")
            else:
                console.print(f"\n[bold yellow]{msg}[/bold yellow]\n")
            continue

        if cleaned.lower() == "jubei - transform":
            # Only toggle when in Jubei mode (ninja or schoolgirl), not Katherine or Komi
            if current is KATHERINE_PERSONALITY:
                console.print(
                    "[bold yellow]Use 'Katherine - Switch - Jubei' first to return to Jubei-Chan.[/bold yellow]"
                )
                continue
            if current is KOMI_PERSONALITY:
                console.print(
                    "[bold yellow]Use 'Komi - Switch - Jubei' first to return to Jubei-Chan.[/bold yellow]"
                )
                continue
            current = (
                SCHOOLGIRL_PERSONALITY
                if current is NINJA_PERSONALITY
                else NINJA_PERSONALITY
            )
            console.print(
                f"\n[bold magenta]* Transformation! *[/bold magenta]\n"
                f"Jubei-Chan is now in [bold green]{current.name}[/bold green]."
            )
            continue

        # Parse "Jubei - language - XX" (e.g. Jubei - language - ja)
        lang_prefix = "jubei - language - "
        if cleaned.lower().startswith(lang_prefix):
            abbrev = cleaned[len(lang_prefix) :].strip().lower()
            if abbrev in SUPPORTED_LANGUAGES:
                current_language = abbrev
                lang_name = SUPPORTED_LANGUAGES[abbrev]
                console.print(
                    f"\n[bold magenta]* Language changed *[/bold magenta]\n"
                    f"Jubei-Chan will now respond in [bold green]{lang_name}[/bold green]."
                )
            else:
                console.print(
                    f"[bold yellow]Unknown language abbreviation: {abbrev}[/bold yellow]. "
                    f"Supported: ja, es, de, ru, en"
                )
            continue

        # Easter eggs: Jubei, Katherine, Komi, or Jubie can trigger any of these
        _egg_prefixes = ("jubei - ", "katherine - ", "komi - ", "jubie - ")

        # Easter egg: Creator credits
        if cleaned.lower() in (p + "creator" for p in _egg_prefixes) or cleaned.lower() in {
            "creator",
            "who - is - your - creator",
        }:
            console.print(
                "\n[bold magenta]The creator of Jubei-Chan AI is a University student from "
                "Lamar UNiversity named Hector Flores or also known as Mighty Senketsu. "
                "He create Me (Jubei-Chan AI and friends) to be your AI assistent buddy "
                "for Linux MInt. I'm here to teach you the world of Linux MInt!!!![/bold magenta]\n"
            )
            continue

        # Easter egg: Open Linux Mint website
        if cleaned.lower() in (p + "mint" for p in _egg_prefixes):
            try:
                webbrowser.open(LINUX_MINT_URL)
                console.print(
                    "\n[bold cyan]* Opening the Linux Mint website in your browser. *[/bold cyan]\n"
                )
            except Exception:
                console.print(
                    "\n[bold red]Could not open the Linux Mint website.[/bold red]\n"
                )
            continue

        # Easter egg: Open Cinnamon themes website
        if cleaned.lower() in (p + "cinnamon" for p in _egg_prefixes):
            try:
                webbrowser.open(CINNAMON_URL)
                console.print(
                    "\n[bold cyan]* Opening the Cinnamon themes website in your browser. *[/bold cyan]\n"
                )
            except Exception:
                console.print(
                    "\n[bold red]Could not open the Cinnamon website.[/bold red]\n"
                )
            continue

        # Easter egg: Tempel (Temple OS theme)
        if cleaned.lower() in (p + "tempel" for p in _egg_prefixes):
            if _play_youtube_url(EASTER_EGG_TEMPEL_URL, console):
                console.print("\n[bold cyan]* Temple OS theme playing *[/bold cyan]")
                console.print("Type [bold]Jubei - Slice[/bold] to stop.\n")
            else:
                console.print("[bold red]Could not open audio.[/bold red]\n")
            continue

        # Easter egg: Tux (Linux mascot)
        if cleaned.lower() in (p + "tux" for p in _egg_prefixes):
            console.print(f"\n[bold green]{TUX_ASCII_ART}[/bold green]\n")
            continue

        # Easter egg: Young Girl (song)
        if cleaned.lower() in (p + "young girl" for p in _egg_prefixes) or cleaned.lower() in (
            p + "young" for p in _egg_prefixes
        ):
            if _play_youtube_url(EASTER_EGG_YOUNG_URL, console):
                console.print("\n[bold cyan]* Young Girl playing *[/bold cyan]")
                console.print("Type [bold]Jubei - Slice[/bold] to stop.\n")
            else:
                console.print("[bold red]Could not open audio.[/bold red]\n")
            continue

        # Easter egg: Kino (A pack of Cigarettes)
        if cleaned.lower() in (p + "kino" for p in _egg_prefixes):
            if _play_youtube_url(EASTER_EGG_KINO_URL, console):
                console.print("\n[bold cyan]* Kino - A pack of Cigarettes playing *[/bold cyan]")
                console.print("Type [bold]Jubei - Slice[/bold] to stop.\n")
            else:
                console.print("[bold red]Could not open audio.[/bold red]\n")
            continue

        # Easter egg: Slice (stop music)
        if cleaned.lower() in (p + "slice" for p in _egg_prefixes):
            if _stop_music():
                console.print("\n[bold magenta]* Music stopped. *[/bold magenta]\n")
            else:
                console.print("\n[bold yellow]No music was playing.[/bold yellow]\n")
            continue

        reply = use_llm_reply(cleaned, current, console, current_language)
        if reply is None:
            reply = offline_reply(cleaned, current)

        if current is KATHERINE_PERSONALITY:
            header = "Katherine"
        elif current is KOMI_PERSONALITY:
            header = "Komi"
        else:
            header = f"Jubei-Chan - {current.name}"
        if Console is None or Markdown is None:
            console.print(f"\n[{header}] {reply}\n")
        else:
            panel = Panel(Markdown(reply), title=header, expand=False)
            console.print(panel)


if __name__ == "__main__":
    main()
