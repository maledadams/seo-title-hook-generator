# Social Media Hook Generator

A small Flask app for generating social media content packs from one topic.

It is built as a homework learning project, not a marketing website. The UI is intentionally simple: one main generator, a result page, login/register pages, and a small dashboard for saved packs.

## What It Does

- Takes a topic and a primary platform
- Generates a content pack for 7 platforms: Twitter, Instagram, TikTok, LinkedIn, YouTube, Facebook, and Pinterest
- Returns 3 fields per platform: `hook`, `body`, and `hashtags`
- Lets logged-in users save generated packs
- Shows loading feedback while forms are submitting
- Falls back to template-based output if Gemini is unavailable or returns invalid JSON

## Stack

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Google GenAI SDK
- SQLite by default
- Plain HTML templates + CSS

## Project Structure

```text
social_media_hook_generator/
|-- app.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- Start-App.cmd
|-- test_env.py
|-- templates/
|   |-- base.html
|   |-- index.html
|   |-- login.html
|   |-- register.html
|   |-- generate.html
|   |-- dashboard.html
|-- static/
|   |-- styles.css
|-- instance/
|   |-- social_media.db
```

## Environment Variables

Create a `.env` file in this folder.

Required:

```env
GOOGLE_API_KEY=your_google_api_key
SECRET_KEY=your_secret_key
```

Generate a secret key with:

```bash
python generate_secret.py
```

Optional:

```env
TWITTER_BEARER_TOKEN=your_twitter_token
DATABASE_URL=
GEMINI_MODEL=gemini-2.5-flash
```

Notes:

- If `GOOGLE_API_KEY` is missing or the model call fails, the app still works using local fallback content.
- SQLite is used automatically if `DATABASE_URL` is empty.
- `instance/` is used for local app data such as the SQLite database.

## Run Locally

### Windows

From the `social_media_hook_generator` folder:

```bat
Start-App.cmd
```

Or manually:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## How To Use

1. Open the home page.
2. Enter a topic.
3. Pick the main platform.
4. Click generate.
5. Review the content pack.
6. Register/login if you want to save it.

## Example Output Shape

```json
{
  "topic": "artificial intelligence",
  "platforms": {
    "twitter": {
      "hook": "What's your take on artificial intelligence?",
      "body": "Just dropped a thread about artificial intelligence. What are your thoughts?",
      "hashtags": ["#artificialintelligence", "#Twitter", "#SocialMedia"]
    },
    "instagram": {
      "hook": "artificial intelligence in focus",
      "body": "Exploring artificial intelligence in depth. What stands out to you most?",
      "hashtags": ["#artificialintelligence", "#Instagram", "#Content"]
    }
  }
}
```

## Main Behavior

- `GET /` shows the generator
- `POST /generate_demo` generates a pack without login
- `POST /generate` generates a pack for logged-in users
- `POST /save_pack` saves a pack
- `GET /dashboard` shows saved packs
- `GET /api/content_pack/<id>` returns saved pack JSON
- `POST /delete_pack/<id>` deletes a saved pack

## Testing

Basic checks:

```bash
python test_env.py
python -m py_compile app.py
```

## Publishing To GitHub

Before pushing:

- Keep `.env` out of git
- Keep `instance/` out of git
- Keep `instance/social_media.db` out of git
- Rotate any API keys that were exposed or shared
- Commit `.env.example`, not `.env`
- Check `git status` before pushing
