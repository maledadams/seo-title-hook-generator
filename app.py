import io
import re
import time
from functools import lru_cache
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
import streamlit as st

#genre

GENRE_POWER_WORDS: Dict[str, List[str]] = {
    "YouTube": [
        "how to","new","best","free","now","easy","secret","proven","ultimate","mistake","fix","faster",
    ],
    "Blogging/SEO": [
        "guide","checklist","template","step-by-step","research-backed","data","examples","mistakes","pitfalls","quickstart","blueprint","essentials",
    ],
    "E-commerce": [
        "save","limited","exclusive","guaranteed","risk-free","lowest","bonus","sale","bundle","upgrade","authentic","verified",
    ],
    "Travel": [
        "hidden gems","bucket list","escape","offbeat","scenic","dreamy","coastal","alpine","foodie","itinerary","insider",
    ],
    "Gaming": [
        "ranked","meta","op","clutch","speedrun","build","loadout","patch","nerf","buff","secrets","glitch",
    ],
    "Beauty/Fashion": [
        "glow","dewy","timeless","capsule","staple","luxe","dupe","flawless","sculpt","boost","routine","runway",
    ],
    "Fitness/Health": [
        "shred","core","mobility","recovery","low-impact","form","macro","habit","energize","rebuild","routine","tracker",
    ],
    "Personal Finance": [
        "fee-free","diversify","recession-ready","index","tax-smart","audit-proof","runway","passive","compounding","hedge","downturn","durable",
    ],
    "Tech/Coding": [
        "from scratch","walkthrough","bugfix","refactor","production","scalable","secure","lightweight","boilerplate","snippet","cli","deploy",
    ],
    "Education/Study": [
        "revision","spaced","cheat sheet","rubric","exemplar","scaffold","annotate","recall","concept map","practice set","walkthrough","recap",
    ],
    "Food/Cooking": [
        "one-pot","crispy","marinate","seasonal","umami","hearty","budget","batch","tender","quick","gluten-free","meal-prep",
    ],
    "Real Estate": [
        "turnkey","curb appeal","walkable","remodeled","light-filled","south-facing","comps","escrow","interest-rate","price drop","off-market","move-in",
    ],
    "Music/Audio": [
        "remaster","stems","preset","mix-ready","ambient","punchy","analog","warm","signature","unreleased","session","setlist",
    ],
    "Podcasts": [
        "uncut","insider","behind the scenes","takeaways","transcript","highlights","deep dive","clips","premiere","candid","unfiltered","recap",
    ],
    "Photo/Video": [
        "b-roll","cinematic","lut","dynamic range","tack sharp","color grade","handheld","workflow","export","presets","timelapse","slo-mo",
    ],
    "Parenting/Family": [
        "screen-free","soothing","routine","meltdown-proof","fuss-less","milestone","developmental","balanced","lunchbox","chore chart","bedtime","sanity-saving",
    ],
    "DIY/Crafts": [
        "no-sew","upcycle","thrifted","budget-friendly","template","step-cut","stain","seal","hack","makeover","pattern","materials list",
    ],
    "Sports": [
        "playbook","clutch","breakdown","highlight","training","drills","conditioning","analytics","scouting","underdog","streak","comeback",
    ],
    "B2B/SaaS": [
        "case study","roi","onboarding","workflow","automate","compliance","audit-ready","integration","roadmap","sla","scale","uptime",
    ],
    "Nonprofit/Impact": [
        "donor-matched","impact report","on the ground","urgent","lifeline","underserved","amplify","volunteer","transparent","accountable","milestone","outcomes",
    ],
}

EVERGREEN_POWER = [
    "you","because","free","new","easy","now","proven","secret","guarantee","simple","exclusive","results",
]

STOPWORDS = set("a an the of for and or to in on with your you from by at as is are be was were it this that".split())

# Weight genre

GENRE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "YouTube": {"keyword": 0.27, "length": 0.20, "novelty": 0.23, "power": 0.18, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Blogging/SEO": {"keyword": 0.34, "length": 0.25, "novelty": 0.12, "power": 0.17, "no_shouting": 0.07, "no_redundancy": 0.05},
    "E-commerce": {"keyword": 0.28, "length": 0.18, "novelty": 0.14, "power": 0.28, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Travel": {"keyword": 0.24, "length": 0.18, "novelty": 0.20, "power": 0.26, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Gaming": {"keyword": 0.22, "length": 0.18, "novelty": 0.28, "power": 0.20, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Beauty/Fashion": {"keyword": 0.26, "length": 0.20, "novelty": 0.18, "power": 0.24, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Fitness/Health": {"keyword": 0.28, "length": 0.22, "novelty": 0.18, "power": 0.20, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Personal Finance": {"keyword": 0.32, "length": 0.24, "novelty": 0.14, "power": 0.18, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Tech/Coding": {"keyword": 0.30, "length": 0.22, "novelty": 0.18, "power": 0.18, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Education/Study": {"keyword": 0.30, "length": 0.22, "novelty": 0.16, "power": 0.20, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Food/Cooking": {"keyword": 0.26, "length": 0.22, "novelty": 0.18, "power": 0.22, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Real Estate": {"keyword": 0.30, "length": 0.22, "novelty": 0.14, "power": 0.22, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Music/Audio": {"keyword": 0.24, "length": 0.20, "novelty": 0.22, "power": 0.22, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Podcasts": {"keyword": 0.26, "length": 0.22, "novelty": 0.18, "power": 0.22, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Photo/Video": {"keyword": 0.26, "length": 0.22, "novelty": 0.20, "power": 0.20, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Parenting/Family": {"keyword": 0.28, "length": 0.22, "novelty": 0.16, "power": 0.22, "no_shouting": 0.07, "no_redundancy": 0.05},
    "DIY/Crafts": {"keyword": 0.28, "length": 0.22, "novelty": 0.16, "power": 0.22, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Sports": {"keyword": 0.24, "length": 0.20, "novelty": 0.24, "power": 0.20, "no_shouting": 0.07, "no_redundancy": 0.05},
    "B2B/SaaS": {"keyword": 0.34, "length": 0.22, "novelty": 0.12, "power": 0.20, "no_shouting": 0.07, "no_redundancy": 0.05},
    "Nonprofit/Impact": {"keyword": 0.30, "length": 0.22, "novelty": 0.14, "power": 0.22, "no_shouting": 0.07, "no_redundancy": 0.05},
}

# Regex + tokenization

RE_NONALNUM = re.compile(r"[^a-z0-9 ]+")
RE_ALLCAPS = re.compile(r"[A-Z]{4,}")

@lru_cache(maxsize=8192)
def tokenize_cached(s: str) -> Tuple[str, ...]:
    s = RE_NONALNUM.sub(" ", s.lower())
    return tuple(w for w in s.split() if w and w not in STOPWORDS)

# Scoring helpers

def soft_range_score(x: int, low: int, high: int, sweet_low: int, sweet_high: int) -> float:
    if sweet_low <= x <= sweet_high:
        return 1.0
    if x < low or x > high:
        return 0.0
    if x < sweet_low:
        return (x - low) / max(1, sweet_low - low)
    return (high - x) / max(1, high - sweet_high)

def title_length_score(title: str) -> float:
    length = len(title)
    return soft_range_score(length, low=28, high=80, sweet_low=42, sweet_high=66)

def keyword_coverage_score(title_lc: str, kws: Tuple[str, ...]) -> float:
    if not kws:
        return 0.5
    matches = sum(1 for k in kws if f" {k} " in f" {title_lc} ")
    return matches / max(1, len(kws))

def power_word_score(title_lc: str, genre: str) -> float:
    base = sum(1 for w in EVERGREEN_POWER if w in title_lc)
    genre_list = GENRE_POWER_WORDS.get(genre, [])
    genre_hits = sum(1 for w in genre_list if w in title_lc)
    count = base + 1.3 * genre_hits
    return min(1.0, count / 3.0)

def shouting_penalty(title: str) -> float:
    caps = RE_ALLCAPS.findall(title)
    return 1.0 - min(1.0, 0.1 * len(caps))

def redundancy_penalty(tokens: Tuple[str, ...]) -> float:
    dup = len(tokens) - len(set(tokens))
    return 1.0 - min(0.2 * max(0, dup), 0.8)

def novelty_score_vs_current(tokens: Tuple[str, ...], current_tokens: Tuple[str, ...]) -> float:
    sa, sb = set(tokens), set(current_tokens)
    if not sa and not sb:
        return 0.0
    j = len(sa & sb) / max(1, len(sa | sb))
    return 1.0 - j

# Dedupe

def _sig(tokens: Tuple[str, ...]) -> frozenset:
    t = list(tokens)
    bigrams = {f"{t[i]} {t[i+1]}" for i in range(len(t) - 1)}
    return frozenset(list(bigrams)[:8])

def dedupe_titles_fast(cands: List[str]) -> List[str]:
    seen_sig = []
    out = []
    for t in cands:
        tok = tokenize_cached(t)
        sg = _sig(tok)
        if any(len(sg & s) >= 3 for s in seen_sig):
            continue
        seen_sig.append(sg)
        out.append(t)
    return out


# Templates

def base_title_templates(topic: str, kw_list: List[str], year: str) -> List[str]:
    base_kw = (kw_list[0] if kw_list else topic).strip()
    short_kw = base_kw.title()
    t = [
        f"{short_kw}: What Actually Works {year}",
        f"How To {short_kw} Without Wasting Time",
        f"{short_kw} Guide For Beginners",
        f"{short_kw} Mistakes That Kill Performance",
        f"Make {short_kw} Work For You",
        f"{short_kw} Checklist You Can Use Today",
        f"{short_kw} Tips Backed By Data",
        f"Stop Guessing. Start {short_kw}",
        f"{short_kw} In Plain English",
        f"From 0 To Results With {short_kw}",
    ]
    for k in kw_list[1:3]:
        kk = k.strip().title()
        t += [f"{short_kw} vs {kk}: Pick The Right Move", f"{kk} With {short_kw}: A Simple Plan"]
    return t

GENRE_TITLE_TEMPLATES: Dict[str, List[str]] = {
    "YouTube": [
        "{kw} Titles That Boost Watch Time",
        "Why Your {kw} Is Underperforming",
        "Fix Your {kw} In One Edit",
        "{kw} Hooks That Actually Work",
    ],
    "Blogging/SEO": [
        "{kw} Keyword Map With Examples",
        "{kw} Template You Can Copy",
        "{kw} Cluster Plan For Traffic",
        "{kw} Outline That Ranks",
    ],
    "E-commerce": [
        "{kw} That Converts Today",
        "{kw} Offer Stack That Sells",
        "Add {kw} And Reduce Drop-off",
        "{kw} Copy That Builds Trust",
    ],
    "Travel": [
        "{kw} Hidden Gems You Can See",
        "{kw} Itinerary That Flows",
        "Skip The Crowds With {kw}",
        "{kw} On A Real Budget",
    ],
    "Gaming": [
        "{kw} Build For This Patch",
        "The New {kw} Meta",
        "{kw} Guide For Ranked",
        "Speedrun {kw} With No RNG",
    ],
    "Beauty/Fashion": [
        "{kw} Routine For A Clean Look",
        "Affordable {kw} Dupes That Win",
        "{kw} Capsule That Works",
        "{kw} You Can Wear Daily",
    ],
    "Fitness/Health": [
        "{kw} Plan That Keeps You Consistent",
        "Form Cues For {kw}",
        "Low Impact {kw} You Can Stick To",
        "{kw} Habit Builder",
    ],
    "Personal Finance": [
        "{kw} Plan That Survives A Downturn",
        "Tax Smart {kw} You Can Apply",
        "Index Based {kw} For Calm",
        "{kw} Without Paying Extra Fees",
    ],
    "Tech/Coding": [
        "{kw} From Scratch",
        "Production Ready {kw} Tutorial",
        "Refactor Your {kw} Safely",
        "Deploy {kw} In Minutes",
    ],
    "Education/Study": [
        "{kw} Cheat Sheet",
        "Study {kw} With Spaced Practice",
        "{kw} Walkthrough With Recall Prompts",
        "Exam Ready {kw} Examples",
    ],
    "Food/Cooking": [
        "{kw} You Can Cook Tonight",
        "One Pot {kw} For Busy Nights",
        "{kw} Meal Prep That Tastes Good",
        "Seasonal {kw} That Feels Fresh",
    ],
    "Real Estate": [
        "{kw} With Real Comps",
        "{kw} That Raises Curb Appeal",
        "{kw} For A Faster Sale",
        "{kw} You Can Do Before Photos",
    ],
    "Music/Audio": [
        "Mix Ready {kw} Settings",
        "Warm And Punchy {kw}",
        "{kw} Preset Pack Walkthrough",
        "Fix Muddy Mixes With {kw}",
    ],
    "Podcasts": [
        "{kw} Highlights You Can Share",
        "Candid {kw} With Takeaways",
        "{kw} Clips That Land",
        "{kw} Recap In Plain Words",
    ],
    "Photo/Video": [
        "Cinematic {kw} You Can Repeat",
        "{kw} Workflow That Saves Time",
        "{kw} Presets With Before After",
        "Make Your {kw} Tack Sharp",
    ],
    "Parenting/Family": [
        "{kw} That Lowers Stress",
        "Bedtime {kw} That Works",
        "Screen Free {kw} For Rainy Days",
        "Lunchbox {kw} You Can Prep",
    ],
    "DIY/Crafts": [
        "Budget Friendly {kw} Makeover",
        "No Sew {kw} That Holds Up",
        "{kw} Pattern You Can Print",
        "Fix Old Stuff With {kw}",
    ],
    "Sports": [
        "{kw} Breakdown With Real Clips",
        "Build A {kw} Playbook",
        "{kw} Drills For Consistency",
        "Comeback Wins With {kw}",
    ],
    "B2B/SaaS": [
        "{kw} Case Study With ROI",
        "Onboard Faster With {kw}",
        "{kw} Workflow That Scales",
        "Audit Ready {kw} In Days",
    ],
    "Nonprofit/Impact": [
        "{kw} That Moves Donors",
        "Transparent {kw} You Can Share",
        "{kw} With Outcomes Not Jargon",
        "{kw} For Underserved Communities",
    ],
}



# Generation core

def title_templates(topic: str, current: str, kw_list: List[str], genre: str, brand_terms: List[str]) -> List[str]:
    year = time.strftime("%Y")
    base_kw = (kw_list[0] if kw_list else topic).strip()
    short_kw = base_kw.title()

    templates = base_title_templates(topic, kw_list, year)

    genre_ts = GENRE_TITLE_TEMPLATES.get(genre, [])
    for g in genre_ts:
        templates.append(g.format(kw=short_kw))

    out = []
    for t in templates:
        t_clean = re.sub(r"\s+", " ", t).strip()
        if not t_clean:
            continue
        for term in brand_terms:
            if term and term.lower() not in t_clean.lower():
                t_clean = f"{t_clean} {term}"
        out.append(t_clean)

    out = dedupe_titles_fast(out)
    return out[:24]

# Overall scoring

def overall_title_score(title: str, current: str, kw_list: List[str], genre: str, weights: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    title_lc = title.lower()
    title_tok = tokenize_cached(title)
    current_tok = tokenize_cached(current)
    kws = tuple(k.strip().lower() for k in kw_list if k.strip())

    s_len = title_length_score(title)
    s_kw = keyword_coverage_score(title_lc, kws)
    s_pw = power_word_score(title_lc, genre)
    s_nv = novelty_score_vs_current(title_tok, current_tok)
    p_sh = shouting_penalty(title)
    p_rd = redundancy_penalty(title_tok)

    w = weights
    score = (
        w["keyword"] * s_kw +
        w["length"] * s_len +
        w["novelty"] * s_nv +
        w["power"] * s_pw +
        w["no_shouting"] * p_sh +
        w["no_redundancy"] * p_rd
    )
    parts = {
        "keyword": s_kw,
        "length": s_len,
        "novelty": s_nv,
        "power": s_pw,
        "no_shouting": p_sh,
        "no_redundancy": p_rd,
    }
    return float(score), parts

def reasons_from_parts(parts: Dict[str, float]) -> str:
    reasons = []
    if parts.get("keyword", 0) >= 0.66:
        reasons.append("high keyword coverage")
    if parts.get("length", 0) >= 0.80:
        reasons.append("ideal length")
    if parts.get("novelty", 0) >= 0.80:
        reasons.append("different from current")
    if parts.get("power", 0) >= 0.66:
        reasons.append("strong power words")
    if parts.get("no_shouting", 1) < 0.9:
        reasons.append("caps reduced")
    if parts.get("no_redundancy", 1) < 0.9:
        reasons.append("trimmed repeats")
    return ", ".join(reasons) or "balanced"


# App

st.set_page_config(page_title="SEO Title and Hook Rewriter", page_icon="📝", layout="wide")
st.title("SEO Title and Hook Rewriter")
st.caption("Pick a genre, add brand terms, upload CSV. Get scored titles, hooks, and reasons.")

# Controls
genre = st.selectbox("Select genre", options=list(GENRE_POWER_WORDS.keys()), index=list(GENRE_POWER_WORDS.keys()).index("YouTube"))
brand_raw = st.text_input("Brand terms to include in every candidate (comma separated)", value="")
force_terms = [t.strip() for t in brand_raw.split(",") if t.strip()]

with st.expander("Weights", expanded=False):
    st.write("Preset weights come from the selected genre. Toggle Advanced to edit.")
    advanced = st.checkbox("Advanced overrides", value=False)
    base_w = GENRE_WEIGHTS.get(genre, GENRE_WEIGHTS["YouTube"]).copy()
    if advanced:
        c1, c2, c3 = st.columns(3)
        c4, c5, c6 = st.columns(3)
        base_w["keyword"] = c1.slider("Keyword", 0.0, 0.6, float(base_w["keyword"]))
        base_w["length"] = c2.slider("Length", 0.0, 0.6, float(base_w["length"]))
        base_w["novelty"] = c3.slider("Novelty", 0.0, 0.6, float(base_w["novelty"]))
        base_w["power"] = c4.slider("Power words", 0.0, 0.6, float(base_w["power"]))
        base_w["no_shouting"] = c5.slider("No shouting", 0.0, 0.6, float(base_w["no_shouting"]))
        base_w["no_redundancy"] = c6.slider("No redundancy", 0.0, 0.6, float(base_w["no_redundancy"]))
        total = sum(base_w.values())
        if total > 0:
            base_w = {k: v / total for k, v in base_w.items()}
    st.json(base_w)

SAMPLE_CSV = """topic,current_title,keywords
YouTube SEO,My YouTube SEO is not working,youtube seo,video titles,watch time
Instagram Reels Hooks,How to write hooks for IG reels,instagram hooks,shorts scripts,engagement
"""

with st.expander("CSV format example", expanded=False):
    st.code(SAMPLE_CSV, language="csv")

file = st.file_uploader("Upload CSV", type=["csv"], accept_multiple_files=False)
if file is None:
    st.info("Using sample rows. Upload your CSV to run on real data.")
    data = pd.read_csv(io.StringIO(SAMPLE_CSV))
else:
    data = pd.read_csv(file)

required_cols = {"topic", "current_title", "keywords"}
missing = required_cols - set(map(str.lower, data.columns))
if missing:
    st.error(f"Missing columns: {', '.join(sorted(missing))}")
    st.stop()

cols_map = {c: c.lower() for c in data.columns}
data = data.rename(columns=cols_map)

limit = st.number_input("Max rows to process", min_value=1, max_value=int(len(data)), value=int(min(200, len(data))))
subset = data.head(int(limit)).copy()
subset = subset.reset_index(drop=True)

progress = st.progress(0)
rows_out = []
hooks_out = []

for ix, row in subset.iterrows():
    topic = str(row["topic"]) if not pd.isna(row["topic"]) else ""
    current = str(row["current_title"]) if not pd.isna(row["current_title"]) else ""
    kw_list = [k.strip() for k in str(row.get("keywords", "")).split(",") if k.strip()]

    cands = title_templates(topic, current, kw_list, genre, force_terms)

    scored = []
    for t in cands:
        s, parts = overall_title_score(t, current, kw_list, genre, base_w)
        scored.append({
            "topic": topic,
            "genre": genre,
            "brand_terms": ", ".join(force_terms) if force_terms else "",
            "current_title": current,
            "candidate_title": t,
            "score": round(s, 4),
            **{f"s_{k}": round(v, 4) for k, v in parts.items()},
            "reason": reasons_from_parts(parts),
        })

    df = pd.DataFrame(scored).sort_values("score", ascending=False).reset_index(drop=True)
    if df.empty:
        continue
    df["row_index"] = [ix] * len(df)
    rows_out.append(df)

    progress.progress((len(rows_out)) / max(1, len(subset)))

if not rows_out:
    st.stop()

results = pd.concat(rows_out, ignore_index=True)

best = results.groupby("row_index").head(2).copy()

left, right = st.columns([2, 3])
with left:
    st.subheader("Top picks")
    st.dataframe(best[["topic","current_title","candidate_title","score","reason"]], use_container_width=True, hide_index=True)

with right:
    st.subheader("All candidates with scores")
    st.dataframe(results.drop(columns=["row_index"]).reset_index(drop=True), use_container_width=True, hide_index=True)

st.subheader("Hooks")
for rec in hooks_out:
    st.markdown(f"**{rec['topic']}**")
    for h in rec["hooks"]:
        st.write(f"• {h}")
    st.markdown("---")

best_csv = best.drop(columns=["row_index"]).to_csv(index=False)
all_csv = results.drop(columns=["row_index"]).to_csv(index=False)

st.download_button("Download top picks CSV", data=best_csv, file_name=f"title_top_picks_{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv", mime="text/csv")
st.download_button("Download all candidates CSV", data=all_csv, file_name=f"title_candidates_{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv", mime="text/csv")

st.caption("Optimized scoring, genre-aware templates and power words, brand term enforcement, and reasons for picks.")

