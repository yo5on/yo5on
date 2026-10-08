<div align="center">

<img src="https://raw.githubusercontent.com/yo5on/yo5on/main/hd-projects.svg" width="620" alt="projects"/>

<samp><b>GITHUB PROFILE SETUP</b></samp>

<samp>github · markdown · github actions · python · vercel · svg</samp>

</div>

---

<div align="center"><samp>How this GitHub profile is built, and how to recreate the same system for your own account.</samp></div>

---

---

<div align="center">
<samp><b>What this profile architecture does</b></samp>
</div>

<samp>The profile is a single `README.md` that GitHub renders on your profile page.</samp>

<samp>Every visual element that needs the page's own typeface is an SVG, because
GitHub strips `<style>`, `style=` and `<script>` from READMEs.

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

There are three kinds of graphic:

| graphic | made by | updated |
|---|---|---|
| `ascii.svg` | `scripts/make_portrait.py` + `scripts/embed_portrait_font.py` | manually, once |
| `hd-*.svg`, `langs.svg` | `scripts/generate_stats.py` | daily, by the workflow |
| `stats.svg`, `streak.svg` | `scripts/generate_stats.py`, called by `api/contributions.py` | live on Vercel; the committed copies are refreshed daily as the fallback |

Everything uses the Python standard library at runtime, an embedded subset of
JetBrains Mono, and no third-party image or statistics service.</samp>

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

1. Create a **public** repository named exactly `<YOUR_USERNAME>` (for example
   `github.com/<YOUR_USERNAME>/<YOUR_USERNAME>`). GitHub treats this name as
   your profile repository.
2. Put `README.md` at the repository root on the default branch. Whatever it
   contains appears at the top of `github.com/<YOUR_USERNAME>`.
3. The workflow in this repository pushes to the branch it runs on, so keep the
   default branch as the one you edit (normally `main`).

Rendering rules that shape this design:

- <samp>Raw HTML is allowed but sanitised: no `<style>`, no `style=` attributes, no</samp>
  `<script>`. Attributes such as `align`, `width` and `alt` survive.
- <samp>Images are proxied by GitHub. Relative paths (`./ascii.svg`) are served from</samp>
  the repository; absolute URLs (the Vercel graphics) are fetched through
  GitHub's image proxy.
- <samp>SVGs are rendered as images, so their embedded CSS and SMIL animation work,</samp>
  but they cannot load external fonts or run scripts.

---

<div align="center">
<samp><b>Profile UI</b></samp>
</div>

The page follows a few rules rather than a template:

- <samp>**One column.** Every graphic is 620 px wide (`WIDTH` in</samp>
  `generate_stats.py`, and `width="620"` in the README). The portrait is
  narrower at 460 px so it reads as the page's cover.
- <samp>**Centred cover, left-aligned body.** The portrait, the contribution total and</samp>
  the links sit inside `<div align="center">`; the sections below are
  left-aligned.
- <samp>**One typeface.** JetBrains Mono is embedded in every SVG. Plain text that</samp>
  should look monospaced (the stack line, project tags) uses `<samp>`, which
  GitHub renders in a monospace face without needing styles.
- <samp>**SVG headings.** Section headings are SVGs (section 6), so they use the same</samp>
  face as the graphics instead of GitHub's sans-serif headings.
- **Projects as text.** Each project is a bold link, a `<samp>` tag line and one
  sentence. No cards or badges.
- <samp>**Restrained colour.** Graphics use a grey palette defined in</samp>
  `generate_stats.py` (`LIGHT` and `DARK`): data ink, emphasis, dimmed labels,
  and hairline rules. Backgrounds are transparent.
- <samp>**Light and dark mode.** Each SVG carries both palettes and switches with an</samp>
  internal `@media (prefers-color-scheme: dark)` rule. Section 13 covers the
  limits of this.
- <samp>**Motion once.** Charts reveal left to right with SMIL animations that freeze</samp>
  at their final frame; nothing loops.

---

<div align="center">
<samp><b>ASCII Portrait Pipeline</b></samp>
</div>

This is a manual, one-time step. Nothing in the workflow or on Vercel touches
`ascii.svg`. The original photo is not part of the repository and is not needed
to run anything else.

What `make_portrait.py` does:

1. Opens the photo and applies an optional crop (`--crop left,top,right,bottom`).
2. Removes the background with `rembg` (ONNX Runtime underneath) and composites
   the subject onto white, so the background maps to blank characters.
3. Evens local contrast with OpenCV (bilateral filter, then CLAHE) and applies
   a darkening curve.
4. Downsamples to 90 columns (`--cols`) and maps each cell's brightness onto the
   13-character ramp `` .`:-=+*cs#%@`` (space is blank).
5. Writes `ascii.svg`: one `<text>` row per line, each revealed by a clip-path
   wipe with a cursor, staggered top to bottom. Ink is `#6e7681`, switching to
   `#c9d1d9` in dark mode.

Then `embed_portrait_font.py` inlines `scripts/fonts/jbmono-ramp.woff2` and
points the SVG at it. This pins the character advance to 0.6 em so the grid
does not shrink on systems whose default monospace is narrower.

Photo advice from the script: use side lighting, crop from chin to just above
the hair, and use a high-resolution source. Small or flat-lit photos produce a
featureless face.

Windows PowerShell:

```powershell
python -m venv .venv-portrait
.\.venv-portrait\Scripts\Activate.ps1
pip install pillow numpy opencv-python-headless rembg onnxruntime
python scripts/make_portrait.py path\to\photo.png --crop LEFT,TOP,RIGHT,BOTTOM --preview
python scripts/embed_portrait_font.py
deactivate
```

Linux/macOS:

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
  to tune the crop.
- <samp>A second positional argument changes the output path (default `ascii.svg`).</samp>
- <samp>`embed_portrait_font.py` is idempotent; running it twice changes nothing.</samp>
- <samp>Keep the virtual environment and the photo out of the repository.</samp>

---

<div align="center">
<samp><b>Custom SVG Heading System</b></samp>
</div>

`draw_heading(word)` in `scripts/generate_stats.py` draws a 620 x 26 SVG: the
word in 16 px semibold JetBrains Mono, followed by a 1 px hairline to the right
edge. The hairline starts after the widest plausible width of the word, so a
fallback font cannot make it overlap the text.

The words come from one tuple in `main()`:

```python
for word in ("about", "stack", "projects", "stats", "about this page"):
    files[f"hd-{word.replace(' ', '-')}.svg"] = draw_heading(word)
```

Each word becomes `hd-<word with spaces replaced by hyphens>.svg`, for example
`hd-about-this-page.svg`. Headings embed only `jbmono-head.woff2`, which
contains the letters `abceghijkoprstu` and space.

To add or rename a heading:

1. Edit the tuple.
2. Check the word's letters are in the heading subset. Any letter that isn't
   falls back to the viewer's monospace; re-subset the font from the
   [JetBrains Mono release](https://github.com/JetBrains/JetBrainsMono) if you
   need it.
3. Run the generator (section 11) and reference the new file in the README
   with `width="620"`.

Markdown headings (`##`) would render in GitHub's own font with GitHub's
underline, and there is no way to restyle them. SVG headings are the only way
to keep the headings in the same face and colours as the graphics.

---

<div align="center">
<samp><b>GitHub Contribution Statistics</b></samp>
</div>

`scripts/generate_stats.py` makes one GraphQL request to
`https://api.github.com/graphql` asking for:

- <samp>`contributionsCollection.contributionCalendar` over the last 365 days. The</samp>
  window is pinned to whole UTC days, so repeated runs on the same day give
  identical output.
- <samp>The user's first 100 **public, owned, non-fork** repositories, with up to 12</samp>
  languages each, ordered by size. Pinning `privacy: PUBLIC` keeps results the
  same no matter which token is used.

From that it computes:

| value | rule |
|---|---|
| total | `totalContributions` from the calendar |
| active days | days with at least one contribution |
| best week | largest weekly sum in the calendar |
| current streak | consecutive active days ending today; a zero today does not break it, because the day is not over |
| longest streak | longest run of active days in the window |
| by bytes | top 5 languages by byte size across those repositories, as a share of the top five |
| by repos | top 5 primary languages (each repository's largest language), as counts |

Ties are sorted by name so equal values never reorder between runs.

Graphics:

- <samp>`stats.svg`: the total, active days, best week, and a weekly sparkline.</samp>
- <samp>`streak.svg`: current and longest streak with their date ranges.</samp>
- <samp>`langs.svg`: two small bar charts, by bytes and by repos.</samp>

Environment variables:

| variable | required | default | meaning |
|---|---|---|---|
| `GITHUB_TOKEN` | yes | none | token used for the GraphQL request |
| `GH_LOGIN` | no | `yo5on` | the user to summarise; always set it to `<YOUR_USERNAME>` |
| `OUT_DIR` | no | current directory | where the SVGs are written; the directory must already exist |

`generate_stats.py` only rewrites a file whose content changed, and prints a
one-line summary plus the list of updated files.

The **fallback** is the committed copy of `stats.svg` and `streak.svg`. The
Vercel function serves it when it cannot reach GitHub (section 9).

---

<div align="center">
<samp><b>GitHub Actions Automation</b></samp>
</div>

The workflow is `.github/workflows/stats.yml`:

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
  UTC, and scheduled runs can start a few minutes late.
- <samp>**Manual runs:** `workflow_dispatch` adds a "Run workflow" button on the</samp>
  Actions tab.
- <samp>**Token:** the built-in `GITHUB_TOKEN`; there's no secret to create.</samp>
  `GH_LOGIN` comes from the repository owner, so it is correct in your fork
  automatically.
- <samp>**Permissions:** `contents: write` is the only permission, needed to push the</samp>
  commit.
- <samp>**Commits:** only the listed generated files are staged, and only when they</samp>
  changed. `stats.svg` usually changes every day because the 365-day window
  moves. The headings normally never change.
- <samp>**Concurrency:** a manual run and a scheduled run queue instead of racing.</samp>
- <samp>**No loops:** pushes made with `GITHUB_TOKEN` do not trigger workflows, and</samp>
  the workflow has no `push` trigger anyway.

Because the workflow declares `contents: write` itself, it can push even if
the repository's default workflow permissions are read-only. Only an
organisation or enterprise policy that caps token permissions would block it.
Actions must be enabled for the repository (Settings -> Actions -> General).

---

<div align="center">
<samp><b>Vercel Dynamic Statistics</b></samp>
</div>

`https://<YOUR_PROJECT>.vercel.app/stats.svg` and `/streak.svg` are produced
per request:

1. **`middleware.ts`** matches exactly `/stats.svg` and `/streak.svg` and
   rewrites them to `/api/contributions?graphic=stats` or `?graphic=streak`.
   It uses `next` and `rewrite` from `@vercel/functions` (pinned in
   `package.json`).
2. **`api/contributions.py`** is a Python function (a
   `BaseHTTPRequestHandler` subclass named `handler`). It imports
   `scripts/generate_stats.py`, fetches once, and draws both graphics from the
   same data.
3. **Caching:**
   - In memory, per function instance, for 15 minutes. The second graphic
     usually comes from memory.
   - Successful responses send `Cache-Control: public, max-age=0, s-maxage=900`,
     so Vercel's edge caches them for 15 minutes and browsers revalidate.
4. **Fallback:** if the fetch fails (no token, GraphQL error, timeout), the
   function serves the last in-memory result if it is under 24 hours old;
   otherwise it serves the committed `stats.svg`/`streak.svg`. Fallbacks are
   sent with `Cache-Control: no-store`. The response is always a 200 SVG, and
   no error text is ever included.
5. **Diagnostics:** every SVG response carries `X-Stats-Source: github`,
   `memory` or `fallback`. Any other `graphic` value returns 404.

`vercel.json` bundles what the function reads at runtime:

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

The generator, the fonts it inlines, and the two fallback SVGs must all be in
`includeFiles`. Anything missing is absent at runtime, and the function falls
back or fails.

With Vercel's Git integration (the default when importing a repository),
every commit to the default branch triggers a new deployment. That includes
the workflow's daily commit, so the bundled fallback stays at most about a day
old.

---

<div align="center">
<samp><b>Deployment</b></samp>
</div>

1. Push the repository to GitHub.
2. In Vercel, choose **Add New -> Project** and import the repository.
3. Settings:
   - Framework preset: **Other**
   - Root directory: the repository root
   - No build command and no output directory
4. Add environment variables (Project -> Settings -> Environment Variables):
   - `GITHUB_TOKEN`: a fine-grained personal access token with read-only access
     to public repositories. No extra permissions are needed, because the query
     only reads public data.
   - `GH_LOGIN`: `<YOUR_USERNAME>`. The function's default is `yo5on`, so this
     must be set.

   The workflow and Vercel use different tokens. Repository data is pinned to
   public repositories, but the contribution calendar can count private
   contributions differently depending on whose token asks and on your
   profile's private-contribution setting. The live graphics and the committed
   fallback can therefore differ slightly.
5. Deploy. Vercel installs `@vercel/functions` from `package.json`, detects the
   Python function under `api/`, and runs `middleware.ts` in front of it.
6. Check the deployment:

   ```bash
   curl -sI https://<YOUR_PROJECT>.vercel.app/stats.svg
   ```

   Expect `200`, `Content-Type: image/svg+xml` and `X-Stats-Source: github`.
   If it says `fallback`, see section 13.
7. Point the README at `https://<YOUR_PROJECT>.vercel.app/stats.svg` and
   `/streak.svg`.

Never commit tokens. `GITHUB_TOKEN` and `GH_LOGIN` live only in Vercel's
settings; the Actions workflow uses its own built-in token.

---

<div align="center">
<samp><b>Local Development</b></samp>
</div>

Clone:

```powershell
git clone https://github.com/<YOUR_USERNAME>/<YOUR_USERNAME>.git
cd <YOUR_USERNAME>
```

The stat generator needs only Python 3 and has no dependencies.

**Generate the graphics.** Write them to a scratch directory to inspect them
without touching the committed files.

Windows PowerShell:

```powershell
$env:GITHUB_TOKEN = "<token>"        # current session only
$env:GH_LOGIN = "<YOUR_USERNAME>"
New-Item -ItemType Directory -Force out | Out-Null
$env:OUT_DIR = "out"
python scripts/generate_stats.py
start out\stats.svg                  # opens in the default browser/viewer
Remove-Item Env:GITHUB_TOKEN
```

Linux/macOS:

```bash
export GITHUB_TOKEN="<token>" GH_LOGIN="<YOUR_USERNAME>"
mkdir -p out
OUT_DIR=out python3 scripts/generate_stats.py
unset GITHUB_TOKEN
```

Leave `OUT_DIR` unset to regenerate the committed files in place. Add `out/`
to `.gitignore` if you keep it.

**Syntax-check the scripts:**

```bash
python -m py_compile scripts/generate_stats.py scripts/make_portrait.py scripts/embed_portrait_font.py api/contributions.py
```

**Run the Vercel function locally.** The handler is a standard-library HTTP
handler, so Python's built-in server can host it from the repository root. The
middleware does not run here, so request the function's query directly.

PowerShell:

```powershell
python -c "from http.server import HTTPServer; from api.contributions import handler; HTTPServer(('127.0.0.1', 8000), handler).serve_forever()"
curl.exe -sI "http://127.0.0.1:8000/?graphic=stats"
```

Linux/macOS: the same two commands, with `curl` instead of `curl.exe`.

- <samp>With `GITHUB_TOKEN` set in that terminal, the response says</samp>
  `X-Stats-Source: github`.
- <samp>Without it, the response says `fallback` and returns the committed SVG.</samp>
- <samp>Stop the server with Ctrl+C.</samp>

---

<div align="center">
<samp><b>Customization</b></samp>
</div>

| what | where |
|---|---|
| username | `GH_LOGIN` in Vercel; the default in `scripts/generate_stats.py` (`main()`) and `api/contributions.py`; links and Vercel URLs in `README.md` |
| links, bio, stack, projects | `README.md` |
| portrait | re-run section 5 with your own photo |
| headings | the tuple in `main()` of `generate_stats.py` (section 6) |
| SVG colours | `LIGHT` and `DARK` in `generate_stats.py`; `FG_LIGHT` and `FG_DARK` in `make_portrait.py` |
| SVG widths | `WIDTH` in `generate_stats.py` and the matching `width` attributes in `README.md` |
| typography | the subsets in `scripts/fonts/`; `scripts/fonts/README.md` lists what each one covers |
| statistics | the GraphQL `QUERY`, `summarise()` and the `draw_*` functions in `generate_stats.py` |
| schedule | `cron` in `.github/workflows/stats.yml` (UTC) |
| Vercel cache | `FRESH_FOR` and `STALE_FOR` in `api/contributions.py`; `s-maxage` in its response header |

If you add a new generated file, add it to `FILES` in the workflow. If the
Vercel function starts reading a new file, add it to `includeFiles` in
`vercel.json`.

---

<div align="center">
<samp><b>Troubleshooting</b></samp>
</div>

**An SVG doesn't update after a commit.** GitHub caches repository images for
a few minutes, and the image proxy caches external ones. Wait, then hard-refresh.
Check the file on GitHub directly to confirm the commit contains the change.

**Stats or streak don't load.**
- <samp>Open `https://<YOUR_PROJECT>.vercel.app/stats.svg` directly.</samp>
- <samp>If it 404s, the middleware didn't run: check that `middleware.ts` is at the</samp>
  repository root and that the deployment installed `@vercel/functions`.
- <samp>If it errors, look at the function logs in Vercel.</samp>

**The fallback keeps appearing** (`X-Stats-Source: fallback`).
- <samp>`GITHUB_TOKEN` is missing or expired in Vercel.</samp>
- <samp>`GH_LOGIN` names the wrong user.</samp>
- <samp>GitHub returned a GraphQL error.</samp>

Fix the variable and redeploy. Environment variable changes apply only to new
deployments.

**GitHub Actions fails.**
- <samp>Push rejected with 403: check that the `permissions:` block is still in</samp>
  the workflow, and that no organisation policy restricts `GITHUB_TOKEN` to
  read-only.
- <samp>Push rejected as non-fast-forward: someone pushed during the run. Run the</samp>
  workflow again.
- <samp>`GraphQL errors` or `no such user`: check that the repository owner is the</samp>
  account you mean to summarise.

**GraphQL authentication failure locally.** `generate_stats.py` exits with
`GITHUB_TOKEN is not set` when the variable is empty. An HTTP 401 means GitHub
rejected the token: it was mistyped, has expired, or was revoked.

**Fonts look wrong.**
- <samp>The SVGs embed their fonts, so they shouldn't depend on the viewer's machine.</samp>
  If a character renders in another face, it isn't in that subset; see
  `scripts/fonts/README.md`.
- <samp>If the portrait looks narrower than intended, `embed_portrait_font.py` wasn't</samp>
  run after regenerating it.

**Portrait generation problems.**
- <samp>`ModuleNotFoundError`: install the five packages from section 5 in the</samp>
  active virtual environment.
- <samp>A washed-out or featureless face: the photo is too small, flat-lit or loosely</samp>
  cropped. Use `--preview` while adjusting `--crop`.
- <samp>The first run pauses while it downloads the model.</samp>

**Dark/light rendering problems.** The SVGs switch palettes with
`prefers-color-scheme`. Inside an `<img>`, browsers can evaluate that from the
browser or OS preference rather than the GitHub theme. If your GitHub theme
differs from your system theme, the graphics can show the other palette. The
way around this is GitHub's `<picture>` element with separate light and dark
files. This repository doesn't do that.

**Broken README images.** Check the path case (GitHub paths are
case-sensitive), check that the file is committed on the default branch, and
for the Vercel graphics, open the URL directly.

---

<div align="center">
<samp><b>Maintenance Checklist</b></samp>
</div>

- <samp>**README:** every `src`/`href` exists; graphics keep `width="620"`; no</samp>
  `<style>` or `style=` (GitHub strips them); the Vercel URLs point at your
  project.
- <samp>**Generator:**</samp>
  - Run it with `OUT_DIR=out` and open every output.
  - Run it twice and confirm the second run prints `updated: nothing`, so the
    workflow won't commit noise.
  - Keep it standard-library only; the Vercel function has no Python
    dependencies.
- <samp>**Workflow:**</samp>
  - `FILES` lists exactly the generated files.
  - Permissions stay at `contents: write`.
  - After editing, trigger it once from the Actions tab.
- <samp>**Vercel API:**</samp>
  - `includeFiles` covers everything `generate_stats.py` reads (the fonts) and
    both fallback SVGs.
  - After deploying, check the `X-Stats-Source` header.
  - Keep `@vercel/functions` pinned and test the middleware after upgrading it.
- <samp>**Generated SVGs:** don't hand-edit them; the next run overwrites them.</samp>
  Change the generator instead.
- <samp>**Fonts:** after re-subsetting, confirm every drawn character is covered and</samp>
  update `scripts/fonts/README.md`. Keep `OFL.txt` alongside the fonts.

---

<div align="center">
<samp><b>Security Notes</b></samp>
</div>

- <samp>No token is stored in the repository. The workflow uses the built-in</samp>
  `GITHUB_TOKEN`, which is scoped to this repository and expires when the job
  ends.
- <samp>The Vercel token belongs in Vercel's environment variables only. Use a</samp>
  fine-grained token with read-only public access and an expiry date, and
  rotate it when it expires.
- <samp>Never paste tokens into the README, commit messages, workflow files or</samp>
  generated SVGs. The generator writes only counts, dates and language names
  into the SVGs.
- <samp>Error details from failed fetches never reach the HTTP response; the function</samp>
  serves the fallback SVG instead.
- <samp>If a token leaks, revoke it on GitHub immediately, then replace it in Vercel</samp>
  and redeploy.

---

<div align="center">
<samp><b>Recreating the Profile From Zero</b></samp>
</div>

1. Create the public repository `<YOUR_USERNAME>/<YOUR_USERNAME>`.
2. Copy this repository's files into it.
3. Edit `README.md`: your bio, stack, projects and links. Leave the Vercel URLs
   for now.
4. Generate your portrait (section 5), or remove the portrait image from the
   README.
5. Change the `GH_LOGIN` defaults in `scripts/generate_stats.py` and
   `api/contributions.py` to your username.
6. Run `generate_stats.py` locally (section 11) to produce your own
   `stats.svg`, `streak.svg`, `langs.svg` and headings, then commit them.
7. Push, then run "refresh stats" once from the Actions tab to confirm the
   workflow can commit.
8. Import the repository into Vercel, set `GITHUB_TOKEN` and `GH_LOGIN`, and
   deploy (section 10).
9. Confirm `curl -sI https://<YOUR_PROJECT>.vercel.app/stats.svg` reports
   `X-Stats-Source: github`.
10. Put your Vercel URLs in the README and push.
11. Open `github.com/<YOUR_USERNAME>` in both light and dark themes.
