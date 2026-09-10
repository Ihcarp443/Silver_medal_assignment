import json
from rag.vectordb import load_vector_db

vectordb = load_vector_db()

query = "What is the women goat rearing scheme?"

filters = {
    "policy_name": "women goat rearing scheme"
}

# Retrieve more documents first
docs = vectordb.similarity_search(
    query=query,
    k=10
)

print(f"Retrieved {len(docs)} documents\n")

print("===== BEFORE FILTERING =====")
for i, doc in enumerate(docs):
    print(f"\nDoc {i+1}")
    print("Policy:", doc.metadata.get("policy_name"))
    print("Sector:", doc.metadata.get("sector"))

print("\n===== APPLYING FILTER =====")

filtered_docs = []

for doc in docs:
    match = True

    for key, value in filters.items():
        metadata_value = str(doc.metadata.get(key, "")).lower()

        if metadata_value != value.lower():
            match = False
            break

    if match:
        filtered_docs.append(doc)

print(f"\nFiltered Docs: {len(filtered_docs)}")

for doc in filtered_docs:
    print(doc.metadata)