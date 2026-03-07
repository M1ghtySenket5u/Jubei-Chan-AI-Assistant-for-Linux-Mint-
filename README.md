# Project Jubei – Jubei-Chan for Linux Mint

Jubei-Chan is a friendly terminal companion for **Linux Mint beginners**.

She has **two split personalities** inspired by a ninja highschool girl archetype and loosley based by Jubei-Chan: THe Ninja Girl

- **Ninja Mode** – calm, focused mentor that explains Linux clearly. You can ask **any question** in Ninja Mode too—general knowledge, life advice, or casual chat—while keeping the calm ninja tone.
- **Highschool Girl Mode** – casual, energetic, and playful but still accurate. In this mode, **you can ask her any question**—not just Linux! She’ll respond to general topics, life advice, hobbies, school, or casual chat while keeping her cheerful highschool girl personality.

You can also switch to **Katherine** or **Komi**. **Katherine** is inspired by [Miyuki Kobayakawa](https://ultimatepopculture.fandom.com/wiki/Miyuki_Kobayakawa) (You're Under Arrest): the brainy, polite, technical genius—punctual, shy, diligent, voice of reason. **Komi** is inspired by [Natsumi Tsujimoto](https://ultimatepopculture.fandom.com/wiki/Natsumi_Tsujimoto) (You're Under Arrest): outgoing, laid-back, fun-loving, and dependable when it matters. Both can answer questions on any topic with full freedom.

Switch between Jubei-Chan’s two personalities:

```text
Jubei - transform
```

Switch to Katherine or Komi, or back to Jubei-Chan:

```text
Jubei - Switch - Katherine    (activates Katherine)
Katherine - Switch - Jubei    (returns to Jubei-Chan in Highschool Girl Mode)
Jubei - Switch - Komi         (activates Komi)
Komi - Switch - Jubei        (returns to Jubei-Chan in Highschool Girl Mode)
```

You can also make Jubei-Chan respond in different languages:

```text
Jubei - language - ja    (Japanese)
Jubei - language - es    (Spanish)
Jubei - language - de    (German)
Jubei - language - ru    (Russian)
Jubei - language - en    (English, default)
```

**Easter eggs** – try these secret commands:

```text
Jubei - Tempel    (plays Temple OS theme)
Jubei - Tux       (shows Tux, the Linux mascot)
Jubei - Young     (plays a song)
Jubei - Slice     (stops any playing music)
```

> Note: Jubei-Chan is loosely inspired by the main character of an anime, but
> this project does **not** reproduce or distribute any copyrighted dialogue
> or story content. She is an original character for educational use.

---

## 1. Features

- **Linux Mint helper for beginners**
  - Explains what Linux is doing in plain language.
  - Breaks down commands you paste into the chat.
  - Points out **dangerous commands** and suggests safer alternatives.

- **Two personalities (split personality)** plus **Katherine** and **Komi**
  - Default: **Ninja Mode** – serious mentor, step-by-step explanations. Users can ask **any question** (not just Linux) with full freedom.
  - Alternate: **Highschool Girl Mode** – more casual, chatty tone. In this mode, Jubei-Chan can answer **any question** (not just Linux) more freely.
  - Switch with: `Jubei - transform`.
  - **Katherine** – inspired by Miyuki Kobayakawa (You're Under Arrest): brainy, polite, technical genius, punctual, shy, diligent, voice of reason. Answers any topic. Switch with: `Jubei - Switch - Katherine` and `Katherine - Switch - Jubei`.
  - **Komi** – inspired by Natsumi Tsujimoto (You're Under Arrest): outgoing, laid-back, fun-loving, dependable when it matters. Answers any topic. Switch with: `Jubei - Switch - Komi` and `Komi - Switch - Jubei`.

- **Multi-language responses**
  - Jubei-Chan can respond in Japanese (ja), Spanish (es), German (de), Russian (ru), or English (en).
  - Use: `Jubei - language - XX` where XX is the language abbreviation.

- **Easter eggs**
  - `Jubei - Tempel` (Temple OS theme), `Jubei - Tux` (Linux mascot), `Jubei - Young` (song), `Jubei - Slice` (stop music).

- **Internal API key for Jubei-Chan**
  - Optional **JUBIE_API_KEY** protection so only you (or your apps) can use her.
  - On first run, if `JUBIE_API_KEY` is not set, Jubei-Chan will generate a key
    and show you how to enable it.

- **External LLM support**
  - If you provide an `OPENAI_API_KEY`, Jubei-Chan will use a powerful model.
  - If you do **not**, she falls back to a simpler offline helper.

- **“Watching” what you do**
  - You can paste your recent terminal commands or describe your task.
  - Jubei-Chan will explain your actions and suggest next steps.

---

## 2. Requirements

- **OS**: Linux Mint (or any Linux that has Python 3.9+).
- **Python**: 3.9 or later.
- **Python packages**: listed in `requirements.txt`.

If you want Jubei-Chan to use a large language model:

- An account and API key for an LLM provider compatible with the `openai` Python
  client (for example, OpenAI).  
- Environment variable: `OPENAI_API_KEY` set to your provider key.

---

## 3. Installation (step-by-step)

All commands below are meant to be run in **your terminal** on Linux Mint.

1. **Go to your home directory (optional but recommended)**

   ```bash
   cd ~
   ```

2. **Move into the `Project Jubei` folder (this repo)**

   If you have placed this folder somewhere else, adjust the path.

   ```bash
   cd "Project Jubei"
   ```

3. **(Recommended) Create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   If `python3` is not found, try `python` instead.

4. **Install the Python dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **(Optional) Create a `.env` file**

   In the `Project Jubei` directory, create a file named `.env`:

   ```bash
   nano .env
   ```

   Example contents:

   ```env
   # If you want Jubei-Chan to use a powerful external model:
   OPENAI_API_KEY=your_openai_or_compatible_key_here

   # (Optional) Lock Jubei-Chan behind an internal API key:
   JUBIE_API_KEY=pick_a_secret_value_here

   # (Optional) Override default model name:
   JUBIE_MODEL=gpt-4o-mini
   ```

   Save and close (`Ctrl+O`, `Enter`, `Ctrl+X` in nano).

---

## 4. Running Jubei-Chan (basic usage)

From inside the `Project Jubei` directory (and with your virtual environment
activated, if you created one):

```bash
python jubie_cli.py
```

On first run:

- If `JUBIE_API_KEY` is **not** set:
  - The app will **generate an internal API key** and show it to you.
  - You can then add it to your `.env` or shell config later.
- If `JUBIE_API_KEY` **is** set:
  - The app will ask you to type the key.
  - Only users (or apps) that know this key can use Jubei-Chan.

You will see a welcome message, something like:

- Current personality (default): **Ninja Mode**
- Instructions to type `Jubei - transform` to switch modes.
- Instructions to type `exit` or `quit` to leave.

Then you simply type messages and press **Enter**.

Examples:

- `What is Linux Mint and how is it different from Windows?`
- `I just ran: sudo apt update && sudo apt upgrade. What did I do?`
- `Explain: ls -la`

---

## 5. Switching personalities – “Jubei - transform”

Jubei-Chan has two modes:

- **Ninja Mode (default)**
  - Calm, teacher-like, step-by-step mentoring.
  - Uses occasional ninja-style metaphors for learning.
  - **Free Q&A:** You can ask **any question** in Ninja Mode—general knowledge, life advice, hobbies, or casual chat—while keeping the calm ninja mentor tone.

- **Highschool Girl Mode**
  - Casual, energetic, more emotional language.
  - Still technically correct, but “chattier”.

To switch between them at any time, type exactly:

```text
Jubei - transform
```

The program will **toggle** between the two personalities and tell you which mode is now active.

### Katherine – "Jubei - Switch - Katherine" / "Katherine - Switch - Jubei"

**Katherine** is a separate character, inspired by [Miyuki Kobayakawa](https://ultimatepopculture.fandom.com/wiki/Miyuki_Kobayakawa) from *You're Under Arrest*. She is:

- Calm, thoughtful, and polite.
- Methodical, analytical, and the voice of reason.
- Punctual, diligent, and level-headed.

She can answer questions on **any topic** with a composed, professional-yet-warm demeanor.

To switch to Katherine:

```text
Jubei - Switch - Katherine
```

To switch back to Jubei-Chan (in Highschool Girl Mode):

```text
Katherine - Switch - Jubei
```

> Note: When Katherine or Komi is active, `Jubei - transform` does nothing. Use `Katherine - Switch - Jubei` or `Komi - Switch - Jubei` to return to Jubei-Chan first.

### Komi – "Jubei - Switch - Komi" / "Komi - Switch - Jubei"

**Komi** is a separate character, inspired by [Natsumi Tsujimoto](https://ultimatepopculture.fandom.com/wiki/Natsumi_Tsujimoto) from *You're Under Arrest*. She is:

- Outgoing, laid-back, and fun-loving.
- Friendly, easy-going, and can be brash or impulsive when excited (but means well).
- Relies on instincts and gut feelings; dependable when it matters.
- Loves food and good times; encourages others with enthusiasm.

She can answer questions on **any topic** with a big-sister or cheerful-friend vibe.

To switch to Komi:

```text
Jubei - Switch - Komi
```

To switch back to Jubei-Chan (in Highschool Girl Mode):

```text
Komi - Switch - Jubei
```

### Changing language – "Jubei - language - XX"

You can make Jubei-Chan respond in different languages. Type:

```text
Jubei - language - ja    (Japanese)
Jubei - language - es    (Spanish)
Jubei - language - de    (German)
Jubei - language - ru    (Russian)
Jubei - language - en    (English, default)
```

After switching, all of Jubei-Chan's replies will be in the chosen language.
*(Requires an LLM; offline mode replies stay in English.)*

### Easter eggs

Jubei-Chan has a few hidden commands for fun:

| Command | What it does |
|---------|--------------|
| `Jubei - Tempel` | Plays the Temple OS theme from YouTube |
| `Jubei - Tux` | Shows Tux, the Linux penguin mascot, as ASCII art |
| `Jubei - Young` | Plays a song from YouTube |
| `Jubei - Slice` | Stops any music that was started by Tempel or Young |

Music playback uses **mpv** if installed (audio-only); otherwise it opens the
YouTube link in your default browser. Type `Jubei - Slice` to stop music when
using mpv. *(If opened in a browser, close the tab to stop.)*

---

## 6. How Jubie “watches” what you do

For safety and privacy, Jubei-Chan does **not** spy on your system by default.
Instead, she “watches” what you are doing when **you share it with her**.

Here are simple ways to do that:

- After you run a command in another terminal, paste it into Jubei:

  ```text
  I just ran: sudo apt install vlc
  ```

- Before you do something risky, ask her:

  ```text
  I’m about to run: rm -rf ~/Downloads/*
  Is this safe? What does it do exactly?
  ```

She will:

- Explain what the command does.
- Warn you if it looks dangerous (for example `rm -rf`).
- Suggest safer commands or backups when possible.

If you want deeper integration later (e.g., automatic shell logging), you can
extend this project to hook into your shell prompt. For now, **manual sharing**
is the simplest and safest approach.

---

## 7. Creating and using Jubei-Chan’s internal API key

Jubei-Chan can be protected by an internal API key so that only authorized
users or tools can use her.

### 7.1 First run (automatic key creation)

- If `JUBIE_API_KEY` is **not set**, on first run Jubei-Chan will:
  - Generate a random key.
  - Print instructions that look like:

  ```text
  Jubei-Chan internal API key created.
  To require this key in future sessions, set the environment variable
  JUBIE_API_KEY=...your_new_key_here...
  ```

- You can then copy that value and store it in:
  - Your `.env` file, or
  - Your shell config (e.g., `~/.bashrc` or `~/.profile`).

### 7.2 Enforcing the key

Once you set `JUBIE_API_KEY` in your environment, the next time you run:

```bash
python jubie_cli.py
```

Jubei-Chan will ask you to type your key:

```text
Enter your JUBIE_API_KEY to continue:
```

If the key is correct, she will start normally.  
If the key is wrong, she exits immediately.

This behaves like a simple **API key for Jubei-Chan herself**, which you can
use if you later build your own tools that talk to her through the CLI.

---

## 8. Using an external LLM (optional but recommended)

If you have network access and an account with an LLM provider compatible with
the `openai` Python client:

1. Put your provider API key in `.env` or your shell:

   ```env
   OPENAI_API_KEY=your_real_key_here
   ```

2. (Optional) Set a model name:

   ```env
   JUBIE_MODEL=gpt-4o-mini
   ```

3. Run:

   ```bash
   python jubie_cli.py
   ```

If everything is configured correctly, Jubei-Chan will:

- Use the external model for detailed, context-rich explanations.
- Follow the personality rules from her system prompt (ninja / highschool girl).

If something goes wrong (missing key, network error, etc.), she automatically
falls back to her **offline helper** mode.

---

## 9. Offline mode behavior

If no `OPENAI_API_KEY` is available or the model call fails, Jubei-Chan:

- Tries to recognize common Linux commands like `ls`, `cd`, `rm`, `apt`, etc.
- Gives a short explanation about:
  - What the command does.
  - Why you might use it.
  - Simple follow-up ideas.

You can still:

- Paste commands and get basic explanations.
- Ask high-level Linux questions (she will answer in a simpler template style).

---

## 10. Extending Project Jubei

Ideas for future improvements:

- Integrate with your shell so each command you run is optionally logged
  and summarized by Jubei-Chan.
- Add more personalities or “training modes” for:
  - Shell scripting,
  - Networking,
  - System administration.

You are free to modify the code in `jubie_cli.py` to suit your learning style.

---

## 11. HTTP API server (advanced)

You can also run Jubei-Chan as a small **HTTP API** so other programs
or scripts can talk to her.

### 11.1 Start the API server

From inside `Project Jubei` (with your virtual environment activated):

```bash
python jubie_api.py
```

By default, the server listens on:

- **Host**: `127.0.0.1`
- **Port**: `8000` (configurable via `JUBIE_API_PORT`)

### 11.2 API key protection

The HTTP API reuses the same `JUBIE_API_KEY` mechanism:

- If `JUBIE_API_KEY` is **not set**:
  - The API does **not** require a key.
  - This is okay for local testing, but less safe if you expose the port.
- If `JUBIE_API_KEY` **is set**:
  - Every request must include the key either:
    - In header: `X-Jubie-Api-Key: YOUR_KEY_HERE`, or
    - In JSON body: `"jubie_api_key": "YOUR_KEY_HERE"`.

Example of setting the key and starting the server:

```bash
export JUBIE_API_KEY=super_secret_value
python jubie_api.py
```

### 11.3 Endpoints

- **GET `/health`**

  - Checks that the server is alive.

  ```bash
  curl -H "X-Jubie-Api-Key: super_secret_value" \
       http://127.0.0.1:8000/health
  ```

- **POST `/chat`**

  - Main chat endpoint.
  - Request body (JSON):

    ```json
    {
      "message": "Explain: ls -la",
      "personality": "ninja"
    }
    ```

    - **`message`**: what the user wants to say to Jubei-Chan (required).
    - **`personality`** (optional): `"ninja"`, `"schoolgirl"`, `"katherine"`, or `"komi"` (default is ninja).
    - **`previous_personality`** (optional): used for stateless transforms (see below).
    - **`language`** (optional): response language – `"en"`, `"ja"`, `"es"`, `"de"`, or `"ru"` (default is en).

  - Typical `curl` example:

    ```bash
    curl -X POST http://127.0.0.1:8000/chat \
      -H "Content-Type: application/json" \
      -H "X-Jubie-Api-Key: super_secret_value" \
      -d '{"message": "Explain: ls -la", "personality": "ninja"}'
    ```

  - Example JSON response:

    ```json
    {
      "reply": "...Jubei-Chan's explanation here...",
      "personality": "Ninja Mode",
      "mode": "ninja",
      "language": "en",
      "used_llm": true
    }
    ```

### 11.4 Changing language via the API

Send a message to change Jubei-Chan's response language:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-Jubie-Api-Key: super_secret_value" \
  -d '{"message": "Jubei - language - ja"}'
```

Response:

```json
{
  "language_change": true,
  "language": "ja",
  "language_name": "Japanese",
  "reply": "*Language changed!* Jubei-Chan will now respond in Japanese. ..."
}
```

Or include `"language": "ja"` in your regular chat requests to get replies in Japanese (and similarly for `es`, `de`, `ru`, or `en`).

### 11.5 Transforming personalities via the API

For CLI use, you type the phrase:

```text
Jubei - transform
```

The API supports a similar flow in a **stateless** way:

1. Your client tracks the last personality label (`"ninja"` or `"schoolgirl"`).
2. When you want to transform, send:

   ```bash
   curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -H "X-Jubie-Api-Key: super_secret_value" \
     -d '{"message": "Jubei - transform", "previous_personality": "ninja"}'
   ```

3. The response will tell you which personality is now active:

   ```json
   {
     "transform": true,
     "personality": "Highschool Girl Mode",
     "mode": "schoolgirl",
     "reply": "*Transformation!* Jubei-Chan is now in Highschool Girl Mode. Send your next question with this personality."
   }
   ```

You can then store `"schoolgirl"` as your new `previous_personality` for
the next API call.

### 11.6 Switching to Katherine via the API

Send one of these messages to switch characters:

- **Switch to Katherine:**
  ```bash
  curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -H "X-Jubie-Api-Key: super_secret_value" \
    -d '{"message": "Jubei - Switch - Katherine"}'
  ```
  Response includes `"character_switch": true`, `"mode": "katherine"`.

- **Switch back to Jubei-Chan:**
  ```bash
  curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -H "X-Jubie-Api-Key: super_secret_value" \
    -d '{"message": "Katherine - Switch - Jubei"}'
  ```
  Response includes `"character_switch": true`, `"mode": "schoolgirl"`.

For subsequent chat requests, send `"personality": "katherine"` or `"personality": "komi"` when talking to Katherine or Komi.

### 11.7 Switching to Komi via the API

- **Switch to Komi:**
  ```bash
  curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -H "X-Jubie-Api-Key: super_secret_value" \
    -d '{"message": "Jubei - Switch - Komi"}'
  ```
  Response includes `"character_switch": true`, `"mode": "komi"`.

- **Switch back to Jubei-Chan:**
  ```bash
  curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -H "X-Jubie-Api-Key: super_secret_value" \
    -d '{"message": "Komi - Switch - Jubei"}'
  ```

---

## 12. Quick recap

- Run Jubei-Chan:

  ```bash
  cd "Project Jubei"
  python jubie_cli.py
  ```

- Switch personalities and characters:

  ```text
  Jubei - transform              (toggle Ninja / Highschool Girl)
  Jubei - Switch - Katherine     (switch to Katherine)
  Katherine - Switch - Jubei     (switch back to Jubei-Chan)
  Jubei - Switch - Komi         (switch to Komi)
  Komi - Switch - Jubei        (switch back to Jubei-Chan)
  ```

- Change language (Japanese, Spanish, German, Russian, or English):

  ```text
  Jubei - language - ja
  Jubei - language - es
  Jubei - language - de
  Jubei - language - ru
  Jubei - language - en
  ```

- Easter eggs: `Jubei - Tempel`, `Jubei - Tux`, `Jubei - Young`, `Jubei - Slice`.

- Protect her with an internal API key:
  - Add `JUBIE_API_KEY=your_secret` to `.env` or your shell.

- Connect to an external AI model:
  - Add `OPENAI_API_KEY=...` and (optionally) `JUBIE_MODEL=...`.

- Optional HTTP API:
  - Start with `python jubie_api.py`.
  - Talk to it via `curl` or your own tools.

- Optional desktop chat window:

  ```bash
  # In one terminal:
  python jubie_api.py

  # In another terminal:
  python jubie_desktop.py
  ```

  - Set `JUBIE_API_URL` if you change the API port or host.
  - Set `JUBIE_API_KEY` to protect both the API and the desktop app.
  - Use the **Switch character** button or type `Jubei - Switch - Katherine` / `Jubei - Switch - Komi` / `Katherine - Switch - Jubei` / `Komi - Switch - Jubei` to cycle between Jubei-Chan, Katherine, and Komi.

Enjoy learning Linux Mint with Jubei-Chan!

