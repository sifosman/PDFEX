import argparse
import logging
from pathlib import Path

from .config import load_config
from .processor import CatalogImporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import catalogue data from PDF into Supabase"
    )
    parser.add_argument("--pdf", type=Path, required=True, help="Path to the catalogue PDF")
    parser.add_argument("--env", type=Path, help="Optional path to .env file")
    parser.add_argument("--start-page", type=int, help="1-based page number to start from")
    parser.add_argument("--end-page", type=int, help="1-based page number to end at")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--log-level", default="INFO", help="Logging level (INFO, DEBUG, etc.)")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s %(message)s")
    config = load_config(str(args.env) if args.env else None)

    importer = CatalogImporter(config)
    importer.run(
        pdf_path=str(args.pdf),
        start_page=args.start_page,
        end_page=args.end_page,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
