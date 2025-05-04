import sys
import logging
import os
import smtplib
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import shutil
from pathlib import Path
import argparse
from dataclasses import dataclass
from typing import List, Dict

CONFIG_PATH = Path(os.getenv('CONFIG_PATH', Path(__file__).parent / 'config.yaml'))

@dataclass
class SmtpConfig:
    email: str
    server: str
    port: int
    password: str

@dataclass
class Config:
    supported_formats: List[str]
    calibre_ingest_folder: Path
    kindle_emails: Dict[str, str]
    smtp: SmtpConfig

# Load configuration
def load_config() -> Config:
    if not CONFIG_PATH.exists():
        logging.error(f"Configuration file not found: {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, 'r') as file:
        data = yaml.safe_load(file)

    config = Config(
        supported_formats=[fmt.upper() for fmt in data['supported_formats']],
        calibre_ingest_folder=Path(data['calibre_ingest_folder']),
        kindle_emails=data['kindle_emails'],
        smtp=SmtpConfig(**data['smtp'])
    )

    config.calibre_ingest_folder.mkdir(parents=True, exist_ok=True)
    return config

# Send email to Kindle
def send_to_kindle(file_path: Path, kindle_email: str, smtp_config: SmtpConfig) -> None:
    msg = MIMEMultipart()
    msg['From'] = smtp_config.email
    msg['To'] = kindle_email
    msg['Subject'] = 'Your Book'

    with open(file_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={file_path.name}')
        msg.attach(part)

    with smtplib.SMTP(smtp_config.server, smtp_config.port) as server:
        server.starttls()
        server.login(smtp_config.email, smtp_config.password)
        server.send_message(msg)

# Check if the file format is supported
def is_supported_format(file_path: Path, supported_formats: List[str]) -> bool:
    ext = file_path.suffix[1:].upper()
    return ext in supported_formats

# Main function
def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Parse arguments
    parser = argparse.ArgumentParser(description="Process torrent completion actions.")
    parser.add_argument('--name', '-N', required=True, help="Name of the torrent")
    parser.add_argument('--labels', '-G', required=True, help="Comma-separated labels")
    parser.add_argument('--file', '-F', required=True, help="Path to the torrent content")
    parser.add_argument('--rm', '-R', action='store_true', help="Remove the ebook file after processing", default=False)
    args = parser.parse_args()

    torrent_name: str = args.name
    torrent_labels: List[str] = args.labels.split(',')
    torrent_path: Path = Path(args.file)

    config = load_config()

    # Validate file format
    if not is_supported_format(torrent_path, config.supported_formats):
        logging.error(f"Unsupported file format for: {torrent_path}")
        return

    try:

        for label in torrent_labels:
            if label == 'Add to Calibre':
                shutil.copy2(torrent_path, config.calibre_ingest_folder)
            elif label.startswith('Send to'):
                kindle_email = config.kindle_emails.get(label.split(' ')[-1])
                if kindle_email:
                    send_to_kindle(torrent_path, kindle_email, config.smtp)
    except Exception as e:
        logging.exception(f"Error processing torrent: {torrent_name}")
        raise e
    else:
        logging.info(f"Successfully processed torrent: {torrent_name}")
        if args.rm:
            try:
                torrent_path.unlink(missing_ok=True)
                logging.info(f"Removed file: {torrent_path}")
            except Exception as e:
                logging.error(f"Failed to remove file: {torrent_path} - {e}")

    logging.info(f"Processed torrent: {torrent_name} with labels: {torrent_labels}")

if __name__ == '__main__':
    main()