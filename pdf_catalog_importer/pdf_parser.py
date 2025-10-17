import io
import re
from typing import List, Optional

import fitz
from PIL import Image

from .models import ParsedProduct, ProductAsset


def _normalize_text(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def _looks_like_product_code(line: str) -> bool:
    normalized = re.sub(r"[^A-Z0-9\- ]", "", line.upper())
    if not normalized or len(normalized) > 24:
        return False
    return any(char.isdigit() for char in normalized) and re.fullmatch(r"[A-Z0-9][A-Z0-9 \-]*", normalized) is not None


def _extract_pack_quantity(text: str) -> Optional[int]:
    match = re.search(r"(\d+)\s+(?:PACKING|PACK|PACKS)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _extract_dimensions(text: str) -> dict:
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*cm", text, re.IGNORECASE)
    if not matches:
        return {}
    keys = ["width", "depth", "height"]
    values = {}
    for idx, number in enumerate(matches[: len(keys)]):
        values[keys[idx]] = {"value": float(number), "unit": "cm"}
    return values


def _extract_feature_lines(lines: List[str], excluded: List[str]) -> List[str]:
    features = []
    excluded_set = {line.upper() for line in excluded if line}
    for line in lines:
        candidate = line.upper()
        if candidate in excluded_set:
            continue
        if len(candidate) <= 40 and re.fullmatch(r"[A-Z0-9&()\- ,.]+", candidate or ""):
            if any(token for token in candidate.split() if len(token) > 2):
                if candidate not in features:
                    features.append(candidate)
    return features


def _extract_assets(page: fitz.Page, product_code: Optional[str]) -> List[ProductAsset]:
    assets: List[ProductAsset] = []
    images = page.get_images(full=True)
    for index, image_info in enumerate(images):
        xref = image_info[0]
        image_dict = page.parent.extract_image(xref)
        image_bytes = image_dict["image"]
        ext = image_dict.get("ext", "png").lower()
        buffer = io.BytesIO(image_bytes)
        with Image.open(buffer) as pil_image:
            if pil_image.mode in ("P", "CMYK", "RGBA", "LA"):
                pil_image = pil_image.convert("RGB")
            normalized_bytes_io = io.BytesIO()
            pil_image.save(normalized_bytes_io, format="PNG")
            normalized_bytes = normalized_bytes_io.getvalue()
        filename = f"{product_code or 'page'}_{index + 1}.png"
        assets.append(
            ProductAsset(
                filename=filename,
                content_type="image/png",
                data=normalized_bytes,
            )
        )
    return assets


class CatalogParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self._doc = fitz.open(pdf_path)

    def __enter__(self) -> "CatalogParser":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __len__(self) -> int:
        return len(self._doc)

    def close(self) -> None:
        if self._doc is not None:
            self._doc.close()
            self._doc = None

    def parse_page(self, page_index: int, default_currency: Optional[str] = None) -> List[ParsedProduct]:
        page = self._doc[page_index]
        text = page.get_text("text")
        lines = [_normalize_text(line) for line in text.splitlines() if _normalize_text(line)]

        product_code = None
        name = None
        subtitle = None
        category = None

        for idx, line in enumerate(lines):
            if _looks_like_product_code(line):
                product_code = line.replace("  ", " ").strip()
                if idx + 1 < len(lines):
                    name = lines[idx + 1]
                if idx + 2 < len(lines):
                    subtitle = lines[idx + 2]
                break

        if lines:
            category = lines[0] if lines[0] != product_code else (lines[1] if len(lines) > 1 else None)

        pack_quantity = _extract_pack_quantity(text)
        dimensions = _extract_dimensions(text)
        features = _extract_feature_lines(lines, [product_code, name, subtitle, category])
        assets = _extract_assets(page, product_code)

        product = ParsedProduct(
            product_code=product_code,
            name=name,
            subtitle=subtitle,
            category=category,
            pack_quantity=pack_quantity,
            price=None,
            currency=default_currency,
            spec_features=features,
            dimensions=dimensions,
            raw_text=text,
            page_number=page_index + 1,
            assets=assets,
        )
        return [product]
