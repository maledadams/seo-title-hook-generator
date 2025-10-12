# SEO Title and Hook Rewriter

A single file Streamlit app that rewrites titles and proposes short hooks from a CSV. It scores each candidate and lets you export two CSVs you can hand to an editor or a client.

## What it does
- Reads a CSV with three headers: `topic`, `current_title`, `keywords`
- Generates fresh title candidates from clean patterns tied to your topic and keywords
- Scores each candidate and shows the sub scores
- Prints hook lines you can paste into intros or scripts
- Exports a top picks CSV and a full candidates CSV

## Who this is for
- People who run channels or blogs and want faster title reviews
- Editors who need a consistent bar during feedback
- Candidates who want a working demo to show in an interview

## How scoring works
The app normalizes each title then computes six pieces. Final score is a weighted blend. These weights match the code in this repo.

- **Keyword coverage** matches against the `keywords` cell. Weight 0.25
- **Length fit** uses a soft range with a sweet spot for readability. Weight 0.22
- **Novelty vs current** compares tokens against `current_title`. Weight 0.20
- **Power words** checks a safe list like easy, proven, best, fast. Weight 0.18
- **No shouting** applies a light penalty for long ALL CAPS tokens. Weight 0.10
- **No redundancy** trims score when words repeat. Weight 0.05

Each row shows the final score and the six sub scores so you can explain picks in review.

## Run it locally
in the folder there is a file named Start-App, click on it and wait for the dependencies to download then open the browser at `http://localhost:8501`

## CSV format
`keywords` is a comma separated list in a single cell.

```csv
topic,current_title,keywords
YouTube SEO,My YouTube SEO is not working,youtube seo,video titles,watch time
Instagram Reels Hooks,How to write hooks for IG reels,instagram hooks,shorts scripts,engagement
```

## Limits
- CSV must include the three headers exactly
- Titles come from templates and may need small edits for brand voice
- Power words list is short by design
- Scores guide review and are not a promise of CTR gains

## Roadmap
- Per niche power words and templates
- Brand terms field that forces required words
- Weight presets per platform
- PDF one pager per row that explains top picks

## License
MIT
