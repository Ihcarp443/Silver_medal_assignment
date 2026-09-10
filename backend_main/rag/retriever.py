from rag.vectordb import load_vector_db

vectordb = load_vector_db()


def retrieve_documents(
    query: str,
    k: int = 5
):

    try:

        docs = vectordb.similarity_search(
            query=query,
            k=k
        )

        return docs

    except Exception:

        return []


from rag.vectordb import load_disease_db, load_scheme_db

disease_vectordb = load_disease_db()
scheme_vectordb = load_scheme_db()


def retrieve_disease_documents(query: str, k: int = 5, crop: str = "", disease: str = ""):
    try:
        conditions = []
        if crop:
            conditions.append({"crop": crop})
        if disease:
            conditions.append({"disease": disease})

        if not conditions:
            filter_dict = None
        elif len(conditions) == 1:
            filter_dict = conditions[0]
        else:
            filter_dict = {"$and": conditions}

        return disease_vectordb.similarity_search(
            query=query,
            k=k,
            filter=filter_dict,
        )
    except Exception as e:
        print(f"Disease retrieval error: {e}")   
        return []

def retrieve_scheme_documents(query: str, k: int = 5, sector: str = ""):
    try:
        # filter_dict = {"sector": sector} if sector else None
        return scheme_vectordb.similarity_search(
            query=query,
            k=k
            # filter=filter_dict,
        )
    except Exception:
        return []


if __name__ == "__main__":
    query = "What is the best fertilizer for wheat?"
    docs = retrieve_documents(query, k=3)
    print(f"Retrieved {len(docs)} documents for query: '{query}'")
    for i, doc in enumerate(docs):
        print(f"Document {i + 1}: {doc.page_content[:200]}...")  