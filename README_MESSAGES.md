# OVZC message publishing — Stage A

This adds a static announcement directory to the existing GitHub Pages site. It **does not** send texts, run AppleScript, or expose recipient data.

## Install

From the existing Git-connected `OVZC_Website_Project` directory, copy the files in this package into the matching relative locations. Do not replace the existing `scripts/build_static_site.py` (it is currently a placeholder). Do not copy this README over your existing README.

## Create a message

Create `messages/data/2026-11-example.json` with contents like:

```json
{
  "id": "2026-11-example",
  "title": "Example announcement",
  "date": "2026-11-01",
  "expires": "2026-11-30",
  "body": "First paragraph of the announcement.\n\nSecond paragraph."
}
```

`expires` is optional. It hides a message from the directory **when the publisher is run on or after the expiration date**; it does not delete the page or automatically update the live site. Dates use `YYYY-MM-DD`. Omit `expires` to keep the message in the directory indefinitely.

For images, copy a PNG/JPEG/WebP/GIF into `docs/messages/images/` and add, for example, `"images": ["koan.png"]` to the JSON. Images are public, like the webpage. No private recipient data belongs in JSON message files.

## Generate and preview

From the project root:

```sh
python3 scripts/publish_messages.py
open docs/messages/index.html
open docs/index.html
```

Inspect generated pages and links before publishing. The directory exists even with zero messages. Message pages have URLs like `https://ojaivalleyzencenter.org/messages/2026-11-example/`.

## Publish (only after review)

```sh
git status
git diff -- docs/index.html
git add docs/index.html docs/messages scripts/publish_messages.py messages/data
git commit -m "Add messages and announcements"
git push origin main
```

Never commit recipient phone numbers, lists, or messaging credentials. This version is **publishing only**. A separate local private sender will later handle preview, recipient selection, AppleScript, and confirmation.

## Notes

- The website is static and public. Unlisted pages are **not private**.
- Generated message pages are not automatically removed if a JSON file is deleted; remove obsolete generated directories deliberately.
- The existing homepage is changed only by one small link in its Special Events section.
- The original `scripts/build_static_site.py` is a placeholder, not a working site generator.
