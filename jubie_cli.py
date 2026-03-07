import os
import subprocess
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
EASTER_EGG_YOUNG_URL = "https://youtu.be/1KeCfeDagCE?si=b8V5S6203OuXMBTC"

TUX_ASCII_ART = r"""
       
                         4MMMMMMMMMMMML
                       4MMMMMMMMMMMMMMMML
                      MMMMMMMMMMMMMMMMMMML
                     4MMMMMMMMMMMMMMMMMMMMM
                    4MMMMMMMMMMMMMMMMMMMMMML
                    MMMMP   MMMMMM   MMMMMMM
                    MMMM MM  MMM  MM  MMMMMM
                    MMMM MM  MMM  MM  MMMMML
                     MMM MP,,,,,,,MM  MMMMMM
                      MM,"          "MMMMMMP
                      MMw           'MMMMMM
                      MM"w         w MMMMMMML
                      MM" w       w " MMMoMMML
                     MMM " wwwwwww "  MMMMMMML
                   MMMP   ".,,,,,,"     MMMMMMMML
                  MMMP                    MMMMMMMML
                MMMMM                      MMMMMMMML
               MMMMM,,-''             ''-,,MMMMMMMMML
              MMMMM                          MMMMMMMMML
             MMMMM                            MMMMMMMMML
            MMMMM                             MMMMMMMMMM
            MMMM                               MMMMMMMMMM
           MMMMM                               MMMMMMMMMML
          MMMMM                                MMMMMMMMMMM
         MMMMMM                                MMMMMMMMMMM
         MMMMMMM                               MMMMMMMMMMM
         """"MMMM                             MMMMMMMMMMP
        "     ""MMM                            MMMMMMMMP
   "" "         "MMMMMM                      """"MMMMMP"""
 "               "MMMMMMM                   ""   """"""   "
 "                ""MMMMMM                 M"             " ""
  "                 "                   MMM"                  "
 "                   "M               MMMM"                   "
 "                    "MM        MMMMMMMMM"                ""
 "                    "MMMMMMMMMMMMMMMMMMM"              """
  """"                "MMMMMMMMMMMMMMMMMM"           """"
      """"""""       MMMMM               "        ""
              """"""""                      """"""" 
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
        "Type [bold]Katherine - Switch - Jubei[/bold] or [bold]Komi - Switch - Jubei[/bold] to return.\n"
        "Type [bold]Jubei - language - XX[/bold] to change language "
        "(ja=Japanese, es=Spanish, de=German, ru=Russian, en=English).\n"
        "Easter eggs: [bold]Jubei - Tempel[/bold], [bold]Jubei - Tux[/bold], "
        "[bold]Jubei - Young[/bold], [bold]Jubei - Slice[/bold] (stop music).\n"
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

        # Easter egg: Jubei - Tempel (Temple OS theme)
        if cleaned.lower() == "jubei - tempel":
            if _play_youtube_url(EASTER_EGG_TEMPEL_URL, console):
                console.print("\n[bold cyan]* Temple OS theme playing *[/bold cyan]")
                console.print("Type [bold]Jubei - Slice[/bold] to stop.\n")
            else:
                console.print("[bold red]Could not open audio.[/bold red]\n")
            continue

        # Easter egg: Jubei - Tux (Linux mascot)
        if cleaned.lower() == "jubei - tux":
            console.print(f"\n[bold green]{TUX_ASCII_ART}[/bold green]\n")
            continue

        # Easter egg: Jubei - Young (Young song)
        if cleaned.lower() == "jubei - young":
            if _play_youtube_url(EASTER_EGG_YOUNG_URL, console):
                console.print("\n[bold cyan]* Young playing *[/bold cyan]")
                console.print("Type [bold]Jubei - Slice[/bold] to stop.\n")
            else:
                console.print("[bold red]Could not open audio.[/bold red]\n")
            continue

        # Easter egg: Jubei - Slice (stop music)
        if cleaned.lower() == "jubei - slice":
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

