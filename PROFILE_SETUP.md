<div align="center">

<samp><b>GITHUB PROFILE SETUP</b></samp>

<samp>github · markdown · github actions · python · vercel · svg</samp>

</div>

---

<div align="center"><samp>How this GitHub profile is built, and how to recreate the same system for your own account.</samp></div>

---

<div align="center">
<samp><b>What this profile architecture does</b></samp>
</div>

<samp>The profile is a single `README.md` that GitHub renders on your profile page.</samp>

<samp>Every visual element that needs the page's own typeface is an SVG, because GitHub strips `<style>`, `style=` and `<script>` from READMEs.</samp>

```
README.md  (rendered on github.com/<YOUR_USERNAME>)
   |
   +-- ascii.svg                one-time generated portrait
   +-- hd-*.svg                 section headings        } generated daily by
   +-- langs.svg                language charts         } GitHub Actions
   |
   +-- https://<YOUR_PROJECT>.vercel.app/stats.svg      } generated per request
   +-- https://<YOUR_PROJECT>.vercel.app/streak.svg     } on Vercel
             |
             v
        middleware.ts  ->  api/contributions.py  ->  scripts/generate_stats.py
                                                          |
                                                          v
                                                  GitHub GraphQL API
```

<samp>There are three kinds of graphic:</samp>

| <samp>graphic</samp> | <samp>made by</samp> | <samp>updated</samp> |
|---|---|---|
| <samp>`ascii.svg`</samp> | <samp>`scripts/make_portrait.py` + `scripts/embed_portrait_font.py`</samp> | <samp>manually, once</samp> |
| <samp>`hd-*.svg`, `langs.svg`</samp> | <samp>`scripts/generate_stats.py`</samp> | <samp>daily, by the workflow</samp> |
| <samp>`stats.svg`, `streak.svg`</samp> | <samp>`scripts/generate_stats.py`, called by `api/contributions.py`</samp> | <samp>live on Vercel; the committed copies are refreshed daily as the fallback</samp> |

<samp>Everything uses the Python standard library at runtime, an embedded subset of JetBrains Mono, and no third-party image or statistics service.</samp>

---

<div align="center">
<samp><b>Repository Structure</b></samp>
</div>

```
.
├── README.md                  the profile page
├── PROFILE_SETUP.md           this document
├── ascii.svg                  ASCII portrait (manual, one-time)
├── hd-about.svg               section headings (generated)
├── hd-stack.svg
├── hd-projects.svg
├── hd-stats.svg
├── hd-about-this-page.svg
├── langs.svg                  top languages (generated)
├── stats.svg                  contribution total + sparkline (generated; Vercel fallback)
├── streak.svg                 current and longest streak (generated; Vercel fallback)
├── api/
│   └── contributions.py       Vercel Python function serving stats/streak
├── middleware.ts              Vercel middleware: /stats.svg, /streak.svg -> the function
├── vercel.json                function config and files bundled with it
├── package.json               one dependency, @vercel/functions, for the middleware
├── .github/workflows/
│   └── stats.yml              daily regeneration and commit
├── .gitignore
└── scripts/
    ├── generate_stats.py      GraphQL fetch + every generated SVG
    ├── make_portrait.py       photo -> ascii.svg
    ├── embed_portrait_font.py inlines the font into ascii.svg
    └── fonts/
        ├── jbmono-400.woff2   regular, basic latin plus · – —
        ├── jbmono-600.woff2   semibold, same characters
        ├── jbmono-head.woff2  semibold, only the heading letters
        ├── jbmono-ramp.woff2  regular, only the portrait's 13 characters
        ├── OFL.txt            font licence
        └── README.md          what each subset covers
```

- <samp>`README.md`: layout, bio, stack, projects, and the image references.</samp>
- <samp>`ascii.svg`: the portrait. Generated once from a photo; not touched by automation.</samp>
- <samp>Generated SVGs: written by `generate_stats.py`. The workflow commits them only when their content changes.</samp>
- <samp>`scripts/`: all generators. `generate_stats.py` has no dependencies; `make_portrait.py` needs the imaging packages in section 5.</samp>
- <samp>`scripts/fonts/`: JetBrains Mono subsets, inlined into the SVGs as base64. An `<img>`-loaded SVG cannot fetch an external font, so inlining is the only way to use a custom face.</samp>
- <samp>`api/`, `middleware.ts`, `vercel.json`, `package.json`: the Vercel deployment that serves `stats.svg` and `streak.svg` with fresh data.</samp>
- <samp>`.github/workflows/`: the scheduled job that regenerates and commits graphics.</samp>

---

<div align="center">
<samp><b>GitHub Profile Repository Setup</b></samp>
</div>

1. <samp>Create a **public** repository named exactly `<YOUR_USERNAME>` (for example</samp>
<samp>`github.com/<YOUR_USERNAME>/<YOUR_USERNAME>`). GitHub treats this name as your profile repository.</samp>
2. <samp>Put `README.md` at the repository root on the default branch. Whatever it</samp>
<samp>contains appears at the top of `github.com/<YOUR_USERNAME>`.</samp>
3. <samp>The workflow in this repository pushes to the branch it runs on, so keep the</samp>
<samp>default branch as the one you edit (normally `main`).</samp>

<samp>Rendering rules that shape this design:</samp>

- <samp>Raw HTML is allowed but sanitised: no `<style>`, no `style=` attributes, no</samp>
<samp>`<script>`. Attributes such as `align`, `width` and `alt` survive.</samp>
- <samp>Images are proxied by GitHub. Relative paths (`./ascii.svg`) are served from</samp>
<samp>the repository; absolute URLs (the Vercel graphics) are fetched through GitHub's image proxy.</samp>
- <samp>SVGs are rendered as images, so their embedded CSS and SMIL animation work,</samp>
<samp>but they cannot load external fonts or run scripts.</samp>

---

<div align="center">
<samp><b>Profile UI</b></samp>
</div>

<samp>The page follows a few rules rather than a template:</samp>

- <samp>**One column.** Every graphic is 620 px wide (`WIDTH` in</samp>
<samp>`generate_stats.py`, and `width="620"` in the README). The portrait is narrower at 460 px so it reads as the page's cover.</samp>
- <samp>**Centred cover, left-aligned body.** The portrait, the contribution total and</samp>
<samp>the links sit inside `<div align="center">`; the sections below are left-aligned.</samp>
- <samp>**One typeface.** JetBrains Mono is embedded in every SVG. Plain text that</samp>
<samp>should look monospaced (the stack line, project tags) uses `<samp>`, which GitHub renders in a monospace face without needing styles.</samp>
- <samp>**SVG headings.** Section headings are SVGs (section 6), so they use the same</samp>
<samp>face as the graphics instead of GitHub's sans-serif headings.</samp>
- <samp>**Projects as text.** Each project is a bold link, a `<samp>` tag line and one</samp>
<samp>sentence. No cards or badges.</samp>
- <samp>**Restrained colour.** Graphics use a grey palette defined in</samp>
<samp>`generate_stats.py` (`LIGHT` and `DARK`): data ink, emphasis, dimmed labels, and hairline rules. Backgrounds are transparent.</samp>
- <samp>**Light and dark mode.** Each SVG carries both palettes and switches with an</samp>
<samp>internal `@media (prefers-color-scheme: dark)` rule. Section 13 covers the limits of this.</samp>
- <samp>**Motion once.** Charts reveal left to right with SMIL animations that freeze</samp>
<samp>at their final frame; nothing loops.</samp>

---

<div align="center">
<samp><b>ASCII Portrait Pipeline</b></samp>
</div>

<samp>This is a manual, one-time step. Nothing in the workflow or on Vercel touches `ascii.svg`. The original photo is not part of the repository and is not needed to run anything else.</samp>

<samp>What `make_portrait.py` does:</samp>

1. <samp>Opens the photo and applies an optional crop (`--crop left,top,right,bottom`).</samp>
2. <samp>Removes the background with `rembg` (ONNX Runtime underneath) and composites</samp>
<samp>the subject onto white, so the background maps to blank characters.</samp>
3. <samp>Evens local contrast with OpenCV (bilateral filter, then CLAHE) and applies</samp>
<samp>a darkening curve.</samp>
4. <samp>Downsamples to 90 columns (`--cols`) and maps each cell's brightness onto the</samp>
<samp>13-character ramp `` .`:-=+*cs#%@`` (space is blank).</samp>
5. <samp>Writes `ascii.svg`: one `<text>` row per line, each revealed by a clip-path</samp>
<samp>wipe with a cursor, staggered top to bottom. Ink is `#6e7681`, switching to `#c9d1d9` in dark mode.</samp>

<samp>Then `embed_portrait_font.py` inlines `scripts/fonts/jbmono-ramp.woff2` and points the SVG at it. This pins the character advance to 0.6 em so the grid does not shrink on systems whose default monospace is narrower.</samp>

<samp>Photo advice from the script: use side lighting, crop from chin to just above the hair, and use a high-resolution source. Small or flat-lit photos produce a featureless face.</samp>

<samp>Windows PowerShell:</samp>

```powershell
python -m venv .venv-portrait
.\.venv-portrait\Scripts\Activate.ps1
pip install pillow numpy opencv-python-headless rembg onnxruntime
python scripts/make_portrait.py path\to\photo.png --crop LEFT,TOP,RIGHT,BOTTOM --preview
python scripts/embed_portrait_font.py
deactivate
```

<samp>Linux/macOS:</samp>

```bash
python3 -m venv .venv-portrait
. .venv-portrait/bin/activate
pip install pillow numpy opencv-python-headless rembg onnxruntime
python3 scripts/make_portrait.py path/to/photo.png --crop LEFT,TOP,RIGHT,BOTTOM --preview
python3 scripts/embed_portrait_font.py
deactivate
```

- <samp>The first run downloads a background-removal model of about 176 MB.</samp>
- <samp>`--preview` also prints the ASCII to the terminal, which is the quickest way</samp>
<samp>to tune the crop.</samp>
- <samp>A second positional argument changes the output path (default `ascii.svg`).</samp>
- <samp>`embed_portrait_font.py` is idempotent; running it twice changes nothing.</samp>
- <samp>Keep the virtual environment and the photo out of the repository.</samp>

---

<div align="center">
<samp><b>Custom SVG Heading System</b></samp>
</div>

<samp>`draw_heading(word)` in `scripts/generate_stats.py` draws a 620 x 26 SVG: the word in 16 px semibold JetBrains Mono, followed by a 1 px hairline to the right edge. The hairline starts after the widest plausible width of the word, so a fallback font cannot make it overlap the text.</samp>

<samp>The words come from one tuple in `main()`:</samp>

```python
for word in ("about", "stack", "projects", "stats", "about this page"):
    files[f"hd-{word.replace(' ', '-')}.svg"] = draw_heading(word)
```

<samp>Each word becomes `hd-<word with spaces replaced by hyphens>.svg`, for example `hd-about-this-page.svg`. Headings embed only `jbmono-head.woff2`, which contains the letters `abceghijkoprstu` and space.</samp>

<samp>To add or rename a heading:</samp>

1. <samp>Edit the tuple.</samp>
2. <samp>Check the word's letters are in the heading subset. Any letter that isn't</samp>
<samp>falls back to the viewer's monospace; re-subset the font from the [JetBrains Mono release](https://github.com/JetBrains/JetBrainsMono) if you need it.</samp>
3. <samp>Run the generator (section 11) and reference the new file in the README</samp>
<samp>with `width="620"`.</samp>

<samp>Markdown headings (`##`) would render in GitHub's own font with GitHub's underline, and there is no way to restyle them. SVG headings are the only way to keep the headings in the same face and colours as the graphics.</samp>

---

<div align="center">
<samp><b>GitHub Contribution Statistics</b></samp>
</div>

<samp>`scripts/generate_stats.py` makes one GraphQL request to `https://api.github.com/graphql` asking for:</samp>

- <samp>`contributionsCollection.contributionCalendar` over the last 365 days. The</samp>
<samp>window is pinned to whole UTC days, so repeated runs on the same day give identical output.</samp>
- <samp>The user's first 100 **public, owned, non-fork** repositories, with up to 12</samp>
<samp>languages each, ordered by size. Pinning `privacy: PUBLIC` keeps results the same no matter which token is used.</samp>

<samp>From that it computes:</samp>

| <samp>value</samp> | <samp>rule</samp> |
|---|---|
| <samp>total</samp> | <samp>`totalContributions` from the calendar</samp> |
| <samp>active days</samp> | <samp>days with at least one contribution</samp> |
| <samp>best week</samp> | <samp>largest weekly sum in the calendar</samp> |
| <samp>current streak</samp> | <samp>consecutive active days ending today; a zero today does not break it, because the day is not over</samp> |
| <samp>longest streak</samp> | <samp>longest run of active days in the window</samp> |
| <samp>by bytes</samp> | <samp>top 5 languages by byte size across those repositories, as a share of the top five</samp> |
| <samp>by repos</samp> | <samp>top 5 primary languages (each repository's largest language), as counts</samp> |

<samp>Ties are sorted by name so equal values never reorder between runs.</samp>

<samp>Graphics:</samp>

- <samp>`stats.svg`: the total, active days, best week, and a weekly sparkline.</samp>
- <samp>`streak.svg`: current and longest streak with their date ranges.</samp>
- <samp>`langs.svg`: two small bar charts, by bytes and by repos.</samp>

<samp>Environment variables:</samp>

| <samp>variable</samp> | <samp>required</samp> | <samp>default</samp> | <samp>meaning</samp> |
|---|---|---|---|
| <samp>`GITHUB_TOKEN`</samp> | <samp>yes</samp> | <samp>none</samp> | <samp>token used for the GraphQL request</samp> |
| <samp>`GH_LOGIN`</samp> | <samp>no</samp> | <samp>`yo5on`</samp> | <samp>the user to summarise; always set it to `<YOUR_USERNAME>`</samp> |
| <samp>`OUT_DIR`</samp> | <samp>no</samp> | <samp>current directory</samp> | <samp>where the SVGs are written; the directory must already exist</samp> |

<samp>`generate_stats.py` only rewrites a file whose content changed, and prints a one-line summary plus the list of updated files.</samp>

<samp>The **fallback** is the committed copy of `stats.svg` and `streak.svg`. The Vercel function serves it when it cannot reach GitHub (section 9).</samp>

---

<div align="center">
<samp><b>GitHub Actions Automation</b></samp>
</div>

<samp>The workflow is `.github/workflows/stats.yml`:</samp>

```yaml
name: refresh stats

on:
  schedule:
    - cron: "30 18 * * *"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: refresh-stats
  cancel-in-progress: false

jobs:
  refresh:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v7

      - name: Draw the stat graphics
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GH_LOGIN: ${{ github.repository_owner }}
        run: python3 scripts/generate_stats.py

      - name: Commit whatever changed
        run: |
          FILES="stats.svg streak.svg langs.svg hd-*.svg"
          if [ -z "$(git status --porcelain -- $FILES)" ]; then
            echo "no change"
            exit 0
          fi
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -- $FILES
          git commit -m "stats: refresh profile graphics"
          git push
```

- <samp>**Schedule:** `30 18 * * *` is 18:30 UTC every day. Cron in Actions is always</samp>
<samp>UTC, and scheduled runs can start a few minutes late.</samp>
- <samp>**Manual runs:** `workflow_dispatch` adds a "Run workflow" button on the</samp>
<samp>Actions tab.</samp>
- <samp>**Token:** the built-in `GITHUB_TOKEN`; there's no secret to create.</samp>
<samp>`GH_LOGIN` comes from the repository owner, so it is correct in your fork automatically.</samp>
- <samp>**Permissions:** `contents: write` is the only permission, needed to push the</samp>
<samp>commit.</samp>
- <samp>**Commits:** only the listed generated files are staged, and only when they</samp>
<samp>changed. `stats.svg` usually changes every day because the 365-day window moves. The headings normally never change.</samp>
- <samp>**Concurrency:** a manual run and a scheduled run queue instead of racing.</samp>
- <samp>**No loops:** pushes made with `GITHUB_TOKEN` do not trigger workflows, and</samp>
<samp>the workflow has no `push` trigger anyway.</samp>

<samp>Because the workflow declares `contents: write` itself, it can push even if the repository's default workflow permissions are read-only. Only an organisation or enterprise policy that caps token permissions would block it. Actions must be enabled for the repository (Settings -> Actions -> General).</samp>

---

<div align="center">
<samp><b>Vercel Dynamic Statistics</b></samp>
</div>

<samp>`https://<YOUR_PROJECT>.vercel.app/stats.svg` and `/streak.svg` are produced per request:</samp>

1. <samp>**`middleware.ts`** matches exactly `/stats.svg` and `/streak.svg` and</samp>
<samp>rewrites them to `/api/contributions?graphic=stats` or `?graphic=streak`. It uses `next` and `rewrite` from `@vercel/functions` (pinned in `package.json`).</samp>
2. <samp>**`api/contributions.py`** is a Python function (a</samp>
<samp>`BaseHTTPRequestHandler` subclass named `handler`). It imports `scripts/generate_stats.py`, fetches once, and draws both graphics from the same data.</samp>
3. <samp>**Caching:**</samp>
- <samp>In memory, per function instance, for 15 minutes. The second graphic</samp>
<samp>usually comes from memory.</samp>
- <samp>Successful responses send `Cache-Control: public, max-age=0, s-maxage=900`,</samp>
<samp>so Vercel's edge caches them for 15 minutes and browsers revalidate.</samp>
4. <samp>**Fallback:** if the fetch fails (no token, GraphQL error, timeout), the</samp>
<samp>function serves the last in-memory result if it is under 24 hours old; otherwise it serves the committed `stats.svg`/`streak.svg`. Fallbacks are sent with `Cache-Control: no-store`. The response is always a 200 SVG, and no error text is ever included.</samp>
5. <samp>**Diagnostics:** every SVG response carries `X-Stats-Source: github`,</samp>
<samp>`memory` or `fallback`. Any other `graphic` value returns 404.</samp>

<samp>`vercel.json` bundles what the function reads at runtime:</samp>

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "functions": {
    "api/contributions.py": {
      "includeFiles": "{stats.svg,streak.svg,scripts/generate_stats.py,scripts/fonts/**}",
      "maxDuration": 10
    }
  }
}
```

<samp>The generator, the fonts it inlines, and the two fallback SVGs must all be in `includeFiles`. Anything missing is absent at runtime, and the function falls back or fails.</samp>

<samp>With Vercel's Git integration (the default when importing a repository), every commit to the default branch triggers a new deployment. That includes the workflow's daily commit, so the bundled fallback stays at most about a day old.</samp>

---

<div align="center">
<samp><b>Deployment</b></samp>
</div>

1. <samp>Push the repository to GitHub.</samp>
2. <samp>In Vercel, choose **Add New -> Project** and import the repository.</samp>
3. <samp>Settings:</samp>
- <samp>Framework preset: **Other**</samp>
- <samp>Root directory: the repository root</samp>
- <samp>No build command and no output directory</samp>
4. <samp>Add environment variables (Project -> Settings -> Environment Variables):</samp>
- <samp>`GITHUB_TOKEN`: a fine-grained personal access token with read-only access</samp>
<samp>to public repositories. No extra permissions are needed, because the query only reads public data.</samp>
- <samp>`GH_LOGIN`: `<YOUR_USERNAME>`. The function's default is `yo5on`, so this</samp>
<samp>must be set.</samp>

<samp>The workflow and Vercel use different tokens. Repository data is pinned to public repositories, but the contribution calendar can count private contributions differently depending on whose token asks and on your profile's private-contribution setting. The live graphics and the committed fallback can therefore differ slightly.</samp>
5. <samp>Deploy. Vercel installs `@vercel/functions` from `package.json`, detects the</samp>
<samp>Python function under `api/`, and runs `middleware.ts` in front of it.</samp>
6. <samp>Check the deployment:</samp>

   ```bash
   curl -sI https://<YOUR_PROJECT>.vercel.app/stats.svg
   ```

<samp>Expect `200`, `Content-Type: image/svg+xml` and `X-Stats-Source: github`. If it says `fallback`, see section 13.</samp>
7. <samp>Point the README at `https://<YOUR_PROJECT>.vercel.app/stats.svg` and</samp>
<samp>`/streak.svg`.</samp>

<samp>Never commit tokens. `GITHUB_TOKEN` and `GH_LOGIN` live only in Vercel's settings; the Actions workflow uses its own built-in token.</samp>

---

<div align="center">
<samp><b>Local Development</b></samp>
</div>

<samp>Clone:</samp>

```powershell
git clone https://github.com/<YOUR_USERNAME>/<YOUR_USERNAME>.git
cd <YOUR_USERNAME>
```

<samp>The stat generator needs only Python 3 and has no dependencies.</samp>

<samp>**Generate the graphics.** Write them to a scratch directory to inspect them without touching the committed files.</samp>

<samp>Windows PowerShell:</samp>

```powershell
$env:GITHUB_TOKEN = "<token>"        # current session only
$env:GH_LOGIN = "<YOUR_USERNAME>"
New-Item -ItemType Directory -Force out | Out-Null
$env:OUT_DIR = "out"
python scripts/generate_stats.py
start out\stats.svg                  # opens in the default browser/viewer
Remove-Item Env:GITHUB_TOKEN
```

<samp>Linux/macOS:</samp>

```bash
export GITHUB_TOKEN="<token>" GH_LOGIN="<YOUR_USERNAME>"
mkdir -p out
OUT_DIR=out python3 scripts/generate_stats.py
unset GITHUB_TOKEN
```

<samp>Leave `OUT_DIR` unset to regenerate the committed files in place. Add `out/` to `.gitignore` if you keep it.</samp>

<samp>**Syntax-check the scripts:**</samp>

```bash
python -m py_compile scripts/generate_stats.py scripts/make_portrait.py scripts/embed_portrait_font.py api/contributions.py
```

<samp>**Run the Vercel function locally.** The handler is a standard-library HTTP handler, so Python's built-in server can host it from the repository root. The middleware does not run here, so request the function's query directly.</samp>

<samp>PowerShell:</samp>

```powershell
python -c "from http.server import HTTPServer; from api.contributions import handler; HTTPServer(('127.0.0.1', 8000), handler).serve_forever()"
curl.exe -sI "http://127.0.0.1:8000/?graphic=stats"
```

<samp>Linux/macOS: the same two commands, with `curl` instead of `curl.exe`.</samp>

- <samp>With `GITHUB_TOKEN` set in that terminal, the response says</samp>
<samp>`X-Stats-Source: github`.</samp>
- <samp>Without it, the response says `fallback` and returns the committed SVG.</samp>
- <samp>Stop the server with Ctrl+C.</samp>

---

<div align="center">
<samp><b>Customization</b></samp>
</div>

| <samp>what</samp> | <samp>where</samp> |
|---|---|
| <samp>username</samp> | <samp>`GH_LOGIN` in Vercel; the default in `scripts/generate_stats.py` (`main()`) and `api/contributions.py`; links and Vercel URLs in `README.md`</samp> |
| <samp>links, bio, stack, projects</samp> | <samp>`README.md`</samp> |
| <samp>portrait</samp> | <samp>re-run section 5 with your own photo</samp> |
| <samp>headings</samp> | <samp>the tuple in `main()` of `generate_stats.py` (section 6)</samp> |
| <samp>SVG colours</samp> | <samp>`LIGHT` and `DARK` in `generate_stats.py`; `FG_LIGHT` and `FG_DARK` in `make_portrait.py`</samp> |
| <samp>SVG widths</samp> | <samp>`WIDTH` in `generate_stats.py` and the matching `width` attributes in `README.md`</samp> |
| <samp>typography</samp> | <samp>the subsets in `scripts/fonts/`; `scripts/fonts/README.md` lists what each one covers</samp> |
| <samp>statistics</samp> | <samp>the GraphQL `QUERY`, `summarise()` and the `draw_*` functions in `generate_stats.py`</samp> |
| <samp>schedule</samp> | <samp>`cron` in `.github/workflows/stats.yml` (UTC)</samp> |
| <samp>Vercel cache</samp> | <samp>`FRESH_FOR` and `STALE_FOR` in `api/contributions.py`; `s-maxage` in its response header</samp> |

<samp>If you add a new generated file, add it to `FILES` in the workflow. If the Vercel function starts reading a new file, add it to `includeFiles` in `vercel.json`.</samp>

---

<div align="center">
<samp><b>Troubleshooting</b></samp>
</div>

<samp>**An SVG doesn't update after a commit.** GitHub caches repository images for a few minutes, and the image proxy caches external ones. Wait, then hard-refresh. Check the file on GitHub directly to confirm the commit contains the change.</samp>

<samp>**Stats or streak don't load.**</samp>
- <samp>Open `https://<YOUR_PROJECT>.vercel.app/stats.svg` directly.</samp>
- <samp>If it 404s, the middleware didn't run: check that `middleware.ts` is at the</samp>
<samp>repository root and that the deployment installed `@vercel/functions`.</samp>
- <samp>If it errors, look at the function logs in Vercel.</samp>

<samp>**The fallback keeps appearing** (`X-Stats-Source: fallback`).</samp>
- <samp>`GITHUB_TOKEN` is missing or expired in Vercel.</samp>
- <samp>`GH_LOGIN` names the wrong user.</samp>
- <samp>GitHub returned a GraphQL error.</samp>

<samp>Fix the variable and redeploy. Environment variable changes apply only to new deployments.</samp>

<samp>**GitHub Actions fails.**</samp>
- <samp>Push rejected with 403: check that the `permissions:` block is still in</samp>
<samp>the workflow, and that no organisation policy restricts `GITHUB_TOKEN` to read-only.</samp>
- <samp>Push rejected as non-fast-forward: someone pushed during the run. Run the</samp>
<samp>workflow again.</samp>
- <samp>`GraphQL errors` or `no such user`: check that the repository owner is the</samp>
<samp>account you mean to summarise.</samp>

<samp>**GraphQL authentication failure locally.** `generate_stats.py` exits with `GITHUB_TOKEN is not set` when the variable is empty. An HTTP 401 means GitHub rejected the token: it was mistyped, has expired, or was revoked.</samp>

<samp>**Fonts look wrong.**</samp>
- <samp>The SVGs embed their fonts, so they shouldn't depend on the viewer's machine.</samp>
<samp>If a character renders in another face, it isn't in that subset; see `scripts/fonts/README.md`.</samp>
- <samp>If the portrait looks narrower than intended, `embed_portrait_font.py` wasn't</samp>
<samp>run after regenerating it.</samp>

<samp>**Portrait generation problems.**</samp>
- <samp>`ModuleNotFoundError`: install the five packages from section 5 in the</samp>
<samp>active virtual environment.</samp>
- <samp>A washed-out or featureless face: the photo is too small, flat-lit or loosely</samp>
<samp>cropped. Use `--preview` while adjusting `--crop`.</samp>
- <samp>The first run pauses while it downloads the model.</samp>

<samp>**Dark/light rendering problems.** The SVGs switch palettes with `prefers-color-scheme`. Inside an `<img>`, browsers can evaluate that from the browser or OS preference rather than the GitHub theme. If your GitHub theme differs from your system theme, the graphics can show the other palette. The way around this is GitHub's `<picture>` element with separate light and dark files. This repository doesn't do that.</samp>

<samp>**Broken README images.** Check the path case (GitHub paths are case-sensitive), check that the file is committed on the default branch, and for the Vercel graphics, open the URL directly.</samp>

---

<div align="center">
<samp><b>Maintenance Checklist</b></samp>
</div>

<samp><b>README</b></samp>

- <samp>Every <code>src</code>/<code>href</code> exists; graphics keep <code>width="620"</code>; no <code>&lt;style&gt;</code> or <code>style=</code> (GitHub strips them); the Vercel URLs point at your project.</samp>

<samp><b>Generator</b></samp>

- <samp>Run it with <code>OUT_DIR=out</code> and open every output.</samp>
- <samp>Run it twice and confirm the second run prints <code>updated: nothing</code>, so the workflow won't commit noise.</samp>
- <samp>Keep it standard-library only; the Vercel function has no Python dependencies.</samp>

<samp><b>Workflow</b></samp>

- <samp><code>FILES</code> lists exactly the generated files.</samp>
- <samp>Permissions stay at <code>contents: write</code>.</samp>
- <samp>After editing, trigger it once from the Actions tab.</samp>

<samp><b>Vercel API</b></samp>

- <samp><code>includeFiles</code> covers everything <code>generate_stats.py</code> reads (the fonts) and both fallback SVGs.</samp>
- <samp>After deploying, check the <code>X-Stats-Source</code> header.</samp>
- <samp>Keep <code>@vercel/functions</code> pinned and test the middleware after upgrading it.</samp>

<samp><b>Generated SVGs</b></samp>

- <samp>Don't hand-edit generated SVGs; the next run overwrites them. Change the generator instead.</samp>

<samp><b>Fonts</b></samp>

- <samp>After re-subsetting, confirm every drawn character is covered and update <code>scripts/fonts/README.md</code>. Keep <code>OFL.txt</code> alongside the fonts.</samp>

---

<div align="center">
<samp><b>Security Notes</b></samp>
</div>

- <samp>No token is stored in the repository. The workflow uses the built-in <code>GITHUB_TOKEN</code>, which is scoped to this repository and expires when the job ends.</samp>
- <samp>The Vercel token belongs in Vercel's environment variables only. Use a fine-grained token with read-only public access and an expiry date, and rotate it when it expires.</samp>
- <samp>Never paste tokens into the README, commit messages, workflow files or generated SVGs. The generator writes only counts, dates and language names into the SVGs.</samp>
- <samp>Error details from failed fetches never reach the HTTP response; the function serves the fallback SVG instead.</samp>
- <samp>If a token leaks, revoke it on GitHub immediately, then replace it in Vercel and redeploy.</samp>

---

<div align="center">
<samp><b>Recreating the Profile From Zero</b></samp>
</div>

<samp>Use the following order to recreate the complete profile system:</samp>

<samp>1. Create the public repository <code>&lt;YOUR_USERNAME&gt;/&lt;YOUR_USERNAME&gt;</code>.</samp>

<samp>2. Copy this repository's files into it.</samp>

<samp>3. Edit <code>README.md</code>: your bio, stack, projects and links. Leave the Vercel URLs for now.</samp>

<samp>4. Generate your portrait (section 5), or remove the portrait image from the README.</samp>

<samp>5. Change the <code>GH_LOGIN</code> defaults in <code>scripts/generate_stats.py</code> and <code>api/contributions.py</code> to your username.</samp>

<samp>6. Run <code>generate_stats.py</code> locally (section 11) to produce your own <code>stats.svg</code>, <code>streak.svg</code>, <code>langs.svg</code> and headings, then commit them.</samp>

<samp>7. Push, then run "refresh stats" once from the Actions tab to confirm the workflow can commit.</samp>

<samp>8. Import the repository into Vercel, set <code>GITHUB_TOKEN</code> and <code>GH_LOGIN</code>, and deploy (section 10).</samp>

<samp>9. Confirm <code>curl -sI https://&lt;YOUR_PROJECT&gt;.vercel.app/stats.svg</code> reports <code>X-Stats-Source: github</code>.</samp>

<samp>10. Put your Vercel URLs in the README and push.</samp>

<samp>11. Open <code>github.com/&lt;YOUR_USERNAME&gt;</code> in both light and dark themes.</samp>
