from langchain_community.vectorstores import FAISS

from rag.embeddings import embeddings


def load_vector_db():

    vectordb = FAISS.load_local(
        "data/Scheme_DB",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectordb

from langchain_chroma import Chroma
from rag.embeddings import embeddings

CHROMA_DIR = "data/chroma_db"


def load_disease_db():
    return Chroma(
        collection_name="disease_kb",
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )


def load_scheme_db():
    return Chroma(
        collection_name="scheme_kb",
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )


def get_disease_retriever():
    return load_disease_db().as_retriever(search_kwargs={"k": 5})


def get_scheme_retriever():
    return load_scheme_db().as_retriever(search_kwargs={"k": 5})


def get_retriever():

    vectordb = load_vector_db()

    return vectordb.as_retriever(
        search_kwargs={"k": 5}
    )