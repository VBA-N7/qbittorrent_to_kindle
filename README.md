# qBittorrent to Kindle

A small Python script that automatically sends books downloaded via qBittorrent to your Kindle or moves them into your Calibre “ingest” folder.

## Features

- Move downloaded file to Calibre ingest folder (`Add to Calibre`)
- Send downloaded file as an email attachment to your Kindle (`Send to <Name>'s Kindle`)

## Requirements

- Python 3.7+
- PyYAML module

Install dependencies:
```bash
pip install pyyaml
```

## Configuration (`config.yaml`)

Place `config.yaml` next to `main.py`, or set its path via the `CONFIG_PATH` environment variable.

Expected fields:

```yaml
supported_formats:
  - PDF
  - EPUB
  - MOBI
  # add more extensions as needed

calibre_ingest_folder: "/path/to/calibre/ingest"

kindle_emails:
  user1: "user1@kindle.com"
  user2: "user2@kindle.com"

smtp:
  server: "smtp.example.com"
  port: 587
  email: "your.email@example.com"
  password: "your_smtp_password"
```

## Usage

```bash
python main.py --name "<Torrent Name>" \
               --labels "Add to Calibre,Send to user1" \
               --file "/path/to/downloaded/book.epub"
```

### Arguments

- `--name` (`-N`): Torrent name
- `--labels` (`-G`): Comma‑separated labels
- `--file` (`-F`): Path to the downloaded file

## qBittorrent Integration

In qBittorrent’s settings under **Run external program on torrent completion**, enter:

```text
python main.py --name "%N" --labels "%G" --file "%F"
```

Make sure to wrap each macro (`%N`, `%G`, `%F`, etc.) in quotes if it may contain spaces.

## Supported Labels

- **Add to Calibre**: moves the book into `calibre_ingest_folder`
- **Send to <Name>'s Kindle**: emails the book to the address defined under `kindle_emails.<Name>`

