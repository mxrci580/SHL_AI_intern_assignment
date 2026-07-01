import json
import sys
from pathlib import Path
from dataclasses import asdict

sys.path.append(str(Path(__file__).parent.parent))
from retriever.models import SHLDocument


def load_catalog(path: Path):
    """Load the raw SHL product catalog, resolving invalid newlines in strings."""
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    import re
    # Match double-quoted strings (handling escaped quotes) and replace raw newlines within them
    def replace_newlines(match):
        return match.group(0).replace("\n", " ").replace("\r", " ")
        
    cleaned_content = re.sub(r'"(?:[^"\\]|\\.)*"', replace_newlines, content)
    return json.loads(cleaned_content)



def normalize_product(product: dict) -> dict:
    """Normalize fields such as duration and boolean values, and perform validation."""
    if not product:
        raise ValueError("Product catalog item cannot be empty or None")
        
    # Critical field validation
    if not product.get("entity_id"):
        raise ValueError("Missing 'entity_id' in product catalog item")
    if not product.get("name"):
        raise ValueError("Missing 'name' in product catalog item")
    if not product.get("link"):
        raise ValueError("Missing 'link' in product catalog item")
        
    normalized = product.copy()
    
    # Normalize duration
    duration = normalized.get("duration", "")
    if duration is None:
        normalized["duration"] = "-"
    else:
        duration = str(duration).strip()
        if duration in ("", "N/A", "TBC", "-", "—"):
            normalized["duration"] = "-"
        else:
            normalized["duration"] = duration
            
    # Normalize languages list
    langs = normalized.get("languages", [])
    if isinstance(langs, str):
        langs = [l.strip() for l in langs.split(",") if l.strip()]
    normalized["languages"] = [l.strip() for l in langs if l.strip()]
    
    # Normalize job_levels list
    job_levels = normalized.get("job_levels", [])
    if isinstance(job_levels, str):
        job_levels = [jl.strip() for jl in job_levels.split(",") if jl.strip()]
    normalized["job_levels"] = [jl.strip() for jl in job_levels if jl.strip()]
    
    # Normalize keys list
    keys = normalized.get("keys", [])
    if isinstance(keys, str):
        keys = [k.strip() for k in keys.split(",") if k.strip()]
    normalized["keys"] = [k.strip() for k in keys if k.strip()]
    
    return normalized



def create_page_content(product: dict) -> str:
    """Create the text that will be embedded."""
    name = product.get("name", "")
    description = product.get("description", "")
    keys = ", ".join(product.get("keys", []))
    job_levels = ", ".join(product.get("job_levels", []))
    
    return (
        f"Name: {name}\n"
        f"Description: {description}\n"
        f"Category: {keys}\n"
        f"Job Levels: {job_levels}"
    )



def create_metadata(product: dict) -> dict:
    """Extract metadata used for filtering."""
    return {
        "duration": product.get("duration", "-"),
        "languages": product.get("languages", []),
        "remote": product.get("remote") == "yes",
        "adaptive": product.get("adaptive") == "yes",
        "url": product.get("link", ""),
        "entity_id": product.get("entity_id", ""),
        "job_levels": product.get("job_levels", [])
    }



def build_documents() -> list[SHLDocument]:
    """Convert all products into SHL documents."""
    # Compute relative path from the project root
    project_root = Path(__file__).parent.parent
    catalog_path = project_root / "data" / "shl_product_catalog.json"
    products = load_catalog(catalog_path)
    
    documents = []
    for prod in products:
        normalized = normalize_product(prod)
        page_content = create_page_content(normalized)
        metadata = create_metadata(normalized)
        doc = SHLDocument(page_content=page_content, metadata=metadata)
        documents.append(doc)
        
    return documents


def save_documents(documents: list[SHLDocument]):
    """Save processed documents to disk."""
    project_root = Path(__file__).parent.parent
    output_path = project_root / "data" / "processed" / "processed_catalog.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    serialized = [asdict(doc) for doc in documents]
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(serialized, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print("Building documents...")
    docs = build_documents()
    print(f"Generated {len(docs)} documents.")
    save_documents(docs)
    print("Documents saved successfully.")