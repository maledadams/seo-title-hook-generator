import json
import os
from datetime import datetime
from pathlib import Path

import google.genai as genai
import tweepy
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)
load_dotenv(BASE_DIR / ".env")

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

database_url = os.getenv("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{INSTANCE_DIR / 'social_media.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

_genai_client = None
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"


PLATFORMS = (
    "twitter",
    "instagram",
    "tiktok",
    "linkedin",
    "youtube",
    "facebook",
    "pinterest",
)

PLATFORM_FALLBACKS = {
    "twitter": {
        "hook": "What's your take on {topic}?",
        "body": "Just dropped a thread about {topic}. What are your thoughts?",
        "hashtags": ["#{slug}", "#Twitter", "#SocialMedia"],
    },
    "instagram": {
        "hook": "{topic} in focus",
        "body": "Exploring {topic} in depth. What stands out to you most?",
        "hashtags": ["#{slug}", "#Instagram", "#Content"],
    },
    "tiktok": {
        "hook": "POV: you discover {topic}",
        "body": "{topic} can become a strong short-form content angle. What part would you watch first?",
        "hashtags": ["#{slug}", "#TikTok", "#Viral"],
    },
    "linkedin": {
        "hook": "3 things I learned about {topic}",
        "body": "Professional insights on {topic}. What has your experience looked like?",
        "hashtags": ["#{slug}", "#LinkedIn", "#Professional"],
    },
    "youtube": {
        "hook": "{topic} explained",
        "body": "Complete guide to {topic}. What would you want covered next?",
        "hashtags": ["#{slug}", "#YouTube", "#Tutorial"],
    },
    "facebook": {
        "hook": "Who else thinks {topic} is worth discussing?",
        "body": "Community discussion about {topic}. Share your point of view.",
        "hashtags": ["#{slug}", "#Facebook", "#Discussion"],
    },
    "pinterest": {
        "hook": "Ultimate {topic} guide",
        "body": "Step-by-step {topic} tutorial. Save it for later.",
        "hashtags": ["#{slug}", "#Pinterest", "#Tutorial"],
    },
}

HASHTAG_FALLBACKS = {
    "twitter": {
        "tech": ["#AI", "#MachineLearning", "#TechNews", "#Innovation", "#Coding"],
        "fitness": ["#Fitness", "#Workout", "#Health", "#Gym", "#Motivation"],
        "food": ["#Foodie", "#Recipe", "#Cooking", "#Yum", "#HealthyEating"],
        "travel": ["#Travel", "#Adventure", "#Wanderlust", "#Vacation", "#Explore"],
        "default": ["#Trending", "#Viral", "#Now", "#Popular", "#Content"],
    },
    "instagram": {
        "tech": ["#Tech", "#Innovation", "#Gadget", "#Future", "#Digital"],
        "fitness": ["#FitFam", "#GymLife", "#Healthy", "#Workout", "#Strong"],
        "food": ["#InstaFood", "#Delicious", "#Yummy", "#Foodstagram", "#Eat"],
        "travel": ["#TravelGram", "#Wanderlust", "#Explore", "#Adventure", "#Vacation"],
        "default": ["#Instagood", "#PhotoOfTheDay", "#Beautiful", "#Happy", "#Creative"],
    },
    "tiktok": {
        "tech": ["#TechTok", "#Innovation", "#Gadget", "#Future", "#Digital"],
        "fitness": ["#FitnessTok", "#GymTok", "#Workout", "#FitCheck", "#GymLife"],
        "food": ["#FoodTok", "#Recipe", "#Cooking", "#Yum", "#ASMR"],
        "travel": ["#TravelTok", "#Wanderlust", "#Explore", "#Adventure", "#Vacation"],
        "default": ["#FYP", "#ForYou", "#Trending", "#Viral", "#Creator"],
    },
    "linkedin": {
        "tech": ["#Technology", "#Innovation", "#DigitalTransformation", "#TechNews", "#Leadership"],
        "fitness": ["#Wellness", "#Health", "#Fitness", "#Motivation", "#PersonalDevelopment"],
        "food": ["#FoodIndustry", "#Culinary", "#Nutrition", "#FoodTech", "#Sustainability"],
        "travel": ["#Travel", "#Tourism", "#BusinessTravel", "#Hospitality", "#Adventure"],
        "default": ["#Networking", "#Career", "#Business", "#Leadership", "#Growth"],
    },
    "youtube": {
        "tech": ["#TechReview", "#Tutorial", "#HowTo", "#Gadget", "#TechNews"],
        "fitness": ["#Workout", "#Fitness", "#Health", "#Exercise", "#Training"],
        "food": ["#Recipe", "#Cooking", "#Food", "#Kitchen", "#Culinary"],
        "travel": ["#Travel", "#Adventure", "#Explore", "#Vacation", "#Tourism"],
        "default": ["#Tutorial", "#Review", "#HowTo", "#Guide", "#Tips"],
    },
    "facebook": {
        "tech": ["#Technology", "#Innovation", "#Tech", "#Digital", "#Gadget"],
        "fitness": ["#Fitness", "#Health", "#Workout", "#Wellness", "#Exercise"],
        "food": ["#Food", "#Recipe", "#Cooking", "#Delicious", "#Yummy"],
        "travel": ["#Travel", "#Vacation", "#Adventure", "#Explore", "#Wanderlust"],
        "default": ["#Community", "#Discussion", "#Friends", "#Life", "#Share"],
    },
    "pinterest": {
        "tech": ["#Tech", "#Gadget", "#Innovation", "#Digital", "#Future"],
        "fitness": ["#Fitness", "#Workout", "#Health", "#Wellness", "#Motivation"],
        "food": ["#Recipe", "#Cooking", "#Food", "#Delicious", "#Yummy"],
        "travel": ["#Travel", "#Adventure", "#Explore", "#Vacation", "#Wanderlust"],
        "default": ["#DIY", "#Inspiration", "#Ideas", "#Creative", "#Style"],
    },
}


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContentPack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("content_packs", lazy=True))

    @property
    def parsed_content(self):
        if not self.content:
            return {}
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            return {}


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def get_genai_client():
    global _genai_client
    if _genai_client is not None:
        return _genai_client

    api_key = (os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        return None

    _genai_client = genai.Client(api_key=api_key)
    return _genai_client


def slugify_topic(topic):
    slug = "".join(ch for ch in topic if ch.isalnum())
    return slug or "Content"


def get_trending_hashtags(niche, platform=None):
    token = (os.getenv("TWITTER_BEARER_TOKEN") or "").strip()
    twitter_client = tweepy.Client(bearer_token=token) if token else None

    if twitter_client and platform == "twitter":
        try:
            # Tweepy v2 does not expose trends for free/basic use consistently.
            pass
        except Exception:
            pass

    platform_map = HASHTAG_FALLBACKS.get(platform or "twitter", HASHTAG_FALLBACKS["twitter"])
    return platform_map.get((niche or "").lower(), platform_map["default"])


def build_fallback_content_pack(topic):
    slug = slugify_topic(topic)
    topic_value = topic or "Untitled topic"
    platforms = {}

    for platform in PLATFORMS:
        template = PLATFORM_FALLBACKS[platform]
        platforms[platform] = {
            "hook": template["hook"].format(topic=topic_value),
            "body": template["body"].format(topic=topic_value),
            "hashtags": [tag.format(slug=slug) for tag in get_trending_hashtags(topic_value, platform)[:5]]
            or [tag.format(slug=slug) for tag in template["hashtags"]],
        }

        if not platforms[platform]["hashtags"]:
            platforms[platform]["hashtags"] = [tag.format(slug=slug) for tag in template["hashtags"]]

    return {"topic": topic_value, "platforms": platforms}


def normalize_platform_content(topic, platform, details):
    fallback = build_fallback_content_pack(topic)["platforms"][platform]
    details = details if isinstance(details, dict) else {}
    hashtags = details.get("hashtags", fallback["hashtags"])

    if isinstance(hashtags, str):
        hashtags = [tag for tag in hashtags.replace(",", " ").split() if tag]
    elif isinstance(hashtags, list):
        hashtags = [str(tag).strip() for tag in hashtags if str(tag).strip()]
    else:
        hashtags = fallback["hashtags"]

    return {
        "hook": str(details.get("hook") or fallback["hook"]).strip(),
        "body": str(details.get("body") or fallback["body"]).strip(),
        "hashtags": hashtags[:8] or fallback["hashtags"],
    }


def normalize_content_pack(topic, raw_pack):
    base = raw_pack if isinstance(raw_pack, dict) else {}
    raw_platforms = base.get("platforms", {}) if isinstance(base.get("platforms"), dict) else {}

    return {
        "topic": str(base.get("topic") or topic or "Untitled topic").strip(),
        "platforms": {
            platform: normalize_platform_content(topic, platform, raw_platforms.get(platform, {}))
            for platform in PLATFORMS
        },
    }


def extract_response_text(response):
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    parts = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            maybe_text = getattr(part, "text", None)
            if maybe_text:
                parts.append(maybe_text)
    return "\n".join(parts).strip()


def generate_content_pack(topic, platform):
    topic = (topic or "").strip() or "Untitled topic"
    client = get_genai_client()
    if client is None:
        return build_fallback_content_pack(topic)

    prompt = f"""Generate a JSON social media content pack for the topic "{topic}".

Return valid JSON only with this shape:
{{
  "topic": "{topic}",
  "platforms": {{
    "twitter": {{"hook": "...", "body": "...", "hashtags": ["#tag"]}},
    "instagram": {{"hook": "...", "body": "...", "hashtags": ["#tag"]}},
    "tiktok": {{"hook": "...", "body": "...", "hashtags": ["#tag"]}},
    "linkedin": {{"hook": "...", "body": "...", "hashtags": ["#tag"]}},
    "youtube": {{"hook": "...", "body": "...", "hashtags": ["#tag"]}},
    "facebook": {{"hook": "...", "body": "...", "hashtags": ["#tag"]}},
    "pinterest": {{"hook": "...", "body": "...", "hashtags": ["#tag"]}}
  }}
}}

Make each platform distinct. Prioritize {platform or "twitter"} slightly, but still fill all platforms.
"""

    try:
        response = client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=prompt,
        )
        content_text = extract_response_text(response)
        if content_text.startswith("```json"):
            content_text = content_text[7:]
        if content_text.endswith("```"):
            content_text = content_text[:-3]
        parsed = json.loads(content_text.strip())
        return normalize_content_pack(topic, parsed)
    except Exception as exc:
        print(f"AI generation failed: {exc}. Falling back to template content.")
        return build_fallback_content_pack(topic)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not username or not email or not password:
            flash("Username, email, and password are required")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/generate_demo", methods=["POST"])
def generate_demo():
    topic = (request.form.get("topic") or "").strip()
    platform = (request.form.get("platform") or "twitter").strip().lower()

    if not topic:
        flash("Please enter a topic before generating content")
        return redirect(url_for("index"))

    content_pack = generate_content_pack(topic, platform)
    return render_template(
        "generate.html",
        content_pack=content_pack,
        content_pack_json=json.dumps(content_pack),
        platform=platform,
        demo_mode=True,
    )


@app.route("/generate", methods=["POST"])
@login_required
def generate():
    topic = (request.form.get("topic") or "").strip()
    platform = (request.form.get("platform") or "twitter").strip().lower()

    if not topic:
        flash("Please enter a topic before generating content")
        return redirect(url_for("index"))

    content_pack = generate_content_pack(topic, platform)
    return render_template(
        "generate.html",
        content_pack=content_pack,
        content_pack_json=json.dumps(content_pack),
        platform=platform,
        demo_mode=False,
    )


@app.route("/save_pack", methods=["POST"])
@login_required
def save_pack():
    content_pack_json = request.form.get("content_pack")
    platform = (request.form.get("platform") or "twitter").strip().lower()

    try:
        content_pack = normalize_content_pack("", json.loads(content_pack_json or ""))
    except json.JSONDecodeError:
        flash("Could not save this content pack because the generated data was invalid")
        return redirect(url_for("index"))

    pack = ContentPack(
        user_id=current_user.id,
        topic=content_pack["topic"],
        platform=platform,
        content=json.dumps(content_pack),
    )
    db.session.add(pack)
    db.session.commit()

    flash("Content pack saved successfully")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    content_packs = (
        ContentPack.query.filter_by(user_id=current_user.id)
        .order_by(ContentPack.created_at.desc())
        .all()
    )
    return render_template("dashboard.html", content_packs=content_packs)


@app.route("/api/content_pack/<int:pack_id>")
@login_required
def get_content_pack(pack_id):
    pack = ContentPack.query.filter_by(id=pack_id, user_id=current_user.id).first()
    if not pack:
        return jsonify({"error": "Content pack not found"}), 404

    content = pack.parsed_content
    if not content:
        return jsonify({"error": "Content pack data is invalid"}), 500

    return jsonify(
        {
            "id": pack.id,
            "topic": pack.topic,
            "content": content,
            "created_at": pack.created_at.isoformat(),
        }
    )


@app.route("/delete_pack/<int:pack_id>", methods=["POST"])
@login_required
def delete_pack(pack_id):
    pack = ContentPack.query.filter_by(id=pack_id, user_id=current_user.id).first()
    if pack:
        db.session.delete(pack)
        db.session.commit()
        flash("Content pack deleted successfully")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
