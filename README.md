# SEO-title-and-hook-rewriter-that-scores-candidates-from-a-CSV-and-exports-top-picks

This app reads a CSV with topic, current_title, and keywords, then generates new title options and short hooks. It scores every candidate on keyword coverage, length fit, novelty vs current, power words, and light penalties for shouting and redundancy. You get a ranked table, a hooks section, and two downloads for review.

# SEO Title and Hook Rewriter

A single file Streamlit app that rewrites titles and proposes hooks from a CSV. It scores each candidate and exports two CSVs you can hand to an editor or client.

## What it does

Reads a CSV with three headers: `topic`, `current_title`, `keywords`
Generates new title candidates from patterns tied to your topic and keywords
Scores each candidate so you can sort by the strongest options
Prints short hook lines you can paste into scripts or intros
Exports a top picks CSV and a full candidates CSV

## Who this is for

You run content for a channel or site and need cleaner titles fast
You review work from freelancers and want a consistent bar
You interview for content roles and want a working demo

## How it scores titles

The app normalizes each title then computes six pieces. Final score is a weighted blend.

**Keyword coverage**
  Matches against the `keywords` cell. Weight 0.25
**Length fit**
  Soft range with a sweet spot for readability. Weight 0.22
**Novelty vs current**
  Jaccard distance against `current_title`. Weight 0.20
**Power words**
  Counts from a safe list like easy and proven. Weight 0.18
**No shouting**
  Penalty for long ALL CAPS tokens. Weight 0.10
**No redundancy**
  Penalty for repeated tokens. Weight 0.05

Every row shows the final score and the six sub scores so you can explain picks in review.

## Run it locally

Pick one path. Both work.

### Option A - lightweight setup

1. Install Python 3.10 or newer
2. Open a terminal in the project folder
3. Create a virtual env

   * Windows PowerShell

     ```powershell
     py -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   * macOS or Linux

     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
4. Install deps

   ```bash
   python -m pip install --upgrade pip
   python -m pip install streamlit pandas numpy
   ```
5. Run the app

   ```bash
   python -m streamlit run "Seo Title And Hook Rewriter — App"
   ```
6. Open the browser at `http://localhost:8501`

### Option B - requirements file

1. Create `requirements.txt`

   ```txt
   streamlit
   pandas
   numpy
   ```
2. Then

   ```bash
   python -m pip install -r requirements.txt
   python -m streamlit run "Seo Title And Hook Rewriter — App"
   ```

## CSV format

`keywords` is a comma separated list in a single cell.

```csv
topic,current_title,keywords
YouTube SEO,My YouTube SEO is not working,youtube seo,video titles,watch time
Instagram Reels Hooks,How to write hooks for IG reels,instagram hooks,shorts scripts,engagement
```

## Limits

* CSV must include the three headers exactly
* Titles are template driven and will not match every brand voice
* Power words list is safe and short by design
* Scores guide review and are not a promise of CTR gains
