from pathlib import Path
from rag.vectorstore import VectorStore

DATA_DIR = Path("data/markdown")

def ingest_if_needed():
    store = VectorStore()

    if store.collection.count() > 0:
        print("✅ Vector database already populated")
        return

    print("📥 Ingesting markdown files...")

    texts = []
    metadatas = []
    ids = []

    for md_file in DATA_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        
        # Get relative path from DATA_DIR for better tracking
        relative_path = md_file.relative_to(DATA_DIR)

        texts.append(content)
        metadatas.append({
            "source": str(relative_path)
        })
        # Use relative path for unique ID (replace separators with underscores)
        ids.append(str(relative_path).replace("\\", "_").replace("/", "_").replace(".md", ""))

    if texts:
        store.add_documents(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Ingested {len(texts)} documents")
    else:
        print("⚠️ No markdown files found to ingest")
