import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class AppConfig:
    supabase_url: str
    supabase_service_key: str
    products_table: str = "products"
    product_images_bucket: str = "product_images"
    default_currency: Optional[str] = None
    checkpoint_path: str = "checkpoints/last_page.json"


def load_config(env_path: Optional[str] = None) -> AppConfig:
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()
    products_table = os.getenv("SUPABASE_PRODUCTS_TABLE", "products").strip()
    product_images_bucket = os.getenv("SUPABASE_IMAGES_BUCKET", "product_images").strip()
    default_currency = os.getenv("DEFAULT_CURRENCY")
    checkpoint_path = os.getenv("CHECKPOINT_PATH", "checkpoints/last_page.json").strip()

    if not supabase_url or not supabase_service_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in the environment or .env file")

    return AppConfig(
        supabase_url=supabase_url,
        supabase_service_key=supabase_service_key,
        products_table=products_table,
        product_images_bucket=product_images_bucket,
        default_currency=default_currency,
        checkpoint_path=checkpoint_path,
    )
