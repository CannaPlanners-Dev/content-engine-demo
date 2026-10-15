# Content engine diagram demo

A standalone interactive diagram. Phase switching, route highlighting, step/player
tracing and appearance controls run locally in the browser. This demo has no
connection to a running content engine and cannot generate or publish content.

Live demo: https://cannaplanners-dev.github.io/content-engine-demo/

## Editing and deployment

The editable Pen design remains in the private project repository. Update/export
the interactive web files deliberately, review them for public suitability, and
copy only the reviewed HTML and four images into `public/`. Saving the Pen design
alone does not regenerate this site. No automatic Pen conversion is configured.

Run `python3 scripts/validate_content_engine_demo.py`, preview with
`python3 -m http.server 8765 --directory public`, then commit and push to `main`.
The Pages workflow publishes only `public/` to the same demo link. All other
repository files are excluded from the site. No secrets are required.

The page uses `noindex,nofollow`, and its source link uses `rel="nofollow"`. These
are cooperative indexing controls, not access security. Do not add robots.txt
Disallow rules that prevent crawlers from reading the directives. Anyone can
view or copy these public files. Google Fonts supplies the existing typography.

To roll back, revert the relevant static-file commit and push to `main`. To take
the demo offline, unpublish this repository’s GitHub Pages site.
