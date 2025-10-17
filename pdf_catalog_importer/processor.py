import json
import logging
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from .config import AppConfig
from .models import ParsedProduct
from .pdf_parser import CatalogParser
from .supabase_client import SupabaseService


logger = logging.getLogger(__name__)


class CatalogImporter:
    def __init__(self, config: AppConfig):
        self.config = config
        self.supabase_service = SupabaseService(config)
        self.checkpoint_file = Path(config.checkpoint_path)
        if not self.checkpoint_file.parent.exists():
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

    def load_checkpoint(self) -> Optional[int]:
        if not self.checkpoint_file.exists():
            return None
        try:
            data = json.loads(self.checkpoint_file.read_text())
            return int(data.get("last_completed_page", 0))
        except Exception as exc:
            logger.warning("Failed to load checkpoint: %s", exc)
            return None

    def save_checkpoint(self, page_number: int) -> None:
        payload = {"last_completed_page": page_number}
        self.checkpoint_file.write_text(json.dumps(payload))

    def run(
        self,
        pdf_path: str,
        start_page: Optional[int] = None,
        end_page: Optional[int] = None,
        resume: bool = False,
    ) -> None:
        start_index = (start_page - 1) if start_page else 0
        if start_index < 0:
            start_index = 0

        with CatalogParser(pdf_path) as parser:
            total_pages = len(parser)
            last_page = (end_page - 1) if end_page else total_pages - 1
            if last_page >= total_pages:
                last_page = total_pages - 1

            if resume:
                checkpoint_page = self.load_checkpoint()
                if checkpoint_page:
                    checkpoint_index = checkpoint_page
                    if checkpoint_index <= last_page:
                        start_index = max(start_index, checkpoint_index)

            page_range = range(start_index, last_page + 1)

            for page_index in tqdm(page_range, desc="Processing pages"):
                page_number = page_index + 1
                products = parser.parse_page(page_index, default_currency=self.config.default_currency)
                for product in products:
                    self._process_product(product)
                self.save_checkpoint(page_number)

    def _process_product(self, product: ParsedProduct) -> None:
        identifier = product.product_code or f"page-{product.page_number}"
        image_urls = self.supabase_service.upload_assets(identifier, product.assets)
        if product.product_code:
            self.supabase_service.upsert_product(product, image_urls)
        else:
            logger.warning(
                "Skipping Supabase upsert for page %s because no product code was detected",
                product.page_number,
            )
