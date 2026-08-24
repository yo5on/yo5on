<img src="./hd-about-this-page.svg" width="620" alt="about this page"/>

This profile is built around a collection of generated SVG graphics and custom<br>
tools designed to keep the page lightweight, consistent, and easy to maintain.

`ascii.svg` is generated from a photo using [`scripts/make_portrait.py`](scripts/make_portrait.py),<br>
which converts the image into a monochrome ASCII portrait. The contribution<br>
statistics and other profile graphics are generated automatically using<br>
[`scripts/generate_stats.py`](scripts/generate_stats.py) and GitHub's GraphQL API.

The stats are refreshed automatically through [GitHub Actions](.github/workflows/stats.yml),<br>
so contribution counts, streaks, language statistics, and the yearly activity map<br>
stay up to date without manually regenerating the graphics.

The SVG graphics use SMIL animations to create the reveal effect while keeping<br>
everything self-contained. No external image or statistics service is required,<br>
so the profile doesn't depend on third-party services to display its graphics.

The page uses JetBrains Mono to keep the typography consistent across the<br>
different SVG graphics. The font is embedded where necessary so the ASCII portrait<br>
maintains its intended character spacing across different viewers.
