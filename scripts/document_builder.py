from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SHLDocument:
    page_content: str
    metadata: Dict[str, Any]