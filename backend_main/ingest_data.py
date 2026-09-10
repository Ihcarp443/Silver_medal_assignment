import os
import json

from langchain_core.documents import Document
from langchain_chroma import Chroma

from rag.embeddings import embeddings


SCHEMES_FOLDER = "data/schemes"
DISEASE_KB_FILE = "data/agri_kb_diseases.json"
CHROMA_DIR = "data/chroma_db"


# ==========================================================
# SCHEME KB
# ==========================================================

def load_scheme_chunks(folder_path):

    all_chunks = []

    for file in os.listdir(folder_path):

        if not file.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, file)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        policy_name = data["policy_name"]
        sector = data["sector"]

        for section, content in data["sections"].items():

            base_metadata = {
                "source": "schemes",
                "category": "scheme",
                "policy_name": policy_name,
                "sector": sector,
                "section": section
            }

            # String section
            if isinstance(content, str):
                all_chunks.append({
                    "text": f"{policy_name} {section}: {content}",
                    "metadata": base_metadata
                })

            # List section
            elif isinstance(content, list):

                if section == "faq":
                    for faq in content:
                        all_chunks.append({
                            "text": (
                                f"{policy_name} FAQ\n"
                                f"Q: {faq['question']}\n"
                                f"A: {faq['answer']}"
                            ),
                            "metadata": {**base_metadata, "section": "faq"}
                        })
                else:
                    combined = "\n".join(f"- {item}" for item in content)
                    all_chunks.append({
                        "text": f"{policy_name} {section}\n{combined}",
                        "metadata": base_metadata
                    })

    return all_chunks


# ==========================================================
# DISEASE KB
# ==========================================================

def load_disease_chunks(json_path):

    with open(json_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    all_chunks = []

    for e in entries:
        text = (
            f"Crop: {e['crop']}\n"
            f"Disease: {e['disease']}\n"
            f"Symptoms: {e['symptoms']}\n"
            f"Organic treatment: {e['treatment_organic']}\n"
            f"Chemical treatment: {e['treatment_chemical']}\n"
            f"Prevention: {e['prevention']}\n"
            f"Weather note: {e['weather_note']}"
        )

        all_chunks.append({
            "text": text,
            "metadata": {
                "source": "agri_kb",
                "category": "disease",
                "crop": e["crop"],
                "disease": e["disease"]
            }
        })

    return all_chunks


# ==========================================================
# SHARED
# ==========================================================

def convert_to_documents(chunks):
    return [
        Document(page_content=chunk["text"], metadata=chunk["metadata"])
        for chunk in chunks
    ]


def build_scheme_db():

    print("Loading scheme files...")
    chunks = load_scheme_chunks(SCHEMES_FOLDER)
    print(f"Loaded {len(chunks)} scheme chunks")

    documents = convert_to_documents(chunks)

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="scheme_kb",
        persist_directory=CHROMA_DIR,
    )

    print(f"Scheme KB saved to {CHROMA_DIR} (collection: scheme_kb)")
    return vectordb


def build_disease_db():

    print("Loading disease KB file...")
    chunks = load_disease_chunks(DISEASE_KB_FILE)
    print(f"Loaded {len(chunks)} disease chunks")

    documents = convert_to_documents(chunks)

    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="disease_kb",
        persist_directory=CHROMA_DIR,
    )

    print(f"Disease KB saved to {CHROMA_DIR} (collection: disease_kb)")
    return vectordb


def build_vectordb():
    build_scheme_db()
    build_disease_db()


if __name__ == "__main__":
    build_vectordb()