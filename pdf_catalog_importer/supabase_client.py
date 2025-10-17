from typing import Iterable, List

from supabase import Client, create_client

from .config import AppConfig
from .models import ParsedProduct, ProductAsset


class SupabaseService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client: Client = create_client(config.supabase_url, config.supabase_service_key)
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        storage = self.client.storage
        buckets = storage.list_buckets()
        bucket_names = {getattr(bucket, "name", None) or getattr(bucket, "id", None) for bucket in buckets}
        bucket_names.discard(None)
        if self.config.product_images_bucket not in bucket_names:
            storage.create_bucket(
                self.config.product_images_bucket,
                options={"public": True},
            )

    def upload_assets(self, product_code: str, assets: Iterable[ProductAsset]) -> List[str]:
        image_urls: List[str] = []
        storage = self.client.storage.from_(self.config.product_images_bucket)
        for asset in assets:
            path = f"{product_code}/{asset.filename}"
            upload_options = {
                "contentType": asset.content_type,
                "cacheControl": "3600",
                "upsert": "true",
            }
            storage.upload(
                path,
                asset.data,
                upload_options,
            )
            public_url = storage.get_public_url(path)
            image_urls.append(public_url)
        return image_urls

    def upsert_product(self, product: ParsedProduct, image_urls: List[str]) -> None:
        data = {
            "product_code": product.product_code,
            "name": product.name,
            "subtitle": product.subtitle,
            "category": product.category,
            "pack_quantity": product.pack_quantity,
            "price": product.price,
            "currency": product.currency,
            "spec_features": product.spec_features,
            "dimensions": product.dimensions,
            "primary_image_url": image_urls[0] if image_urls else None,
            "image_urls": image_urls,
            "page_number": product.page_number,
            "raw_text": product.raw_text,
        }
        self.client.table(self.config.products_table).upsert(data, on_conflict="product_code").execute()
