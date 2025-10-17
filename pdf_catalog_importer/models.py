from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ProductAsset:
    filename: str
    content_type: str
    data: bytes


@dataclass
class ParsedProduct:
    product_code: Optional[str]
    name: Optional[str]
    subtitle: Optional[str]
    category: Optional[str]
    pack_quantity: Optional[int]
    price: Optional[float]
    currency: Optional[str]
    spec_features: List[str] = field(default_factory=list)
    dimensions: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    page_number: int = 0
    assets: List[ProductAsset] = field(default_factory=list)
