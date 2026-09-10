from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEndpoint
)

from dotenv import load_dotenv
import os

load_dotenv()
# print("HF TOKEN:", os.getenv("HF_TOKEN"))
llm = HuggingFaceEndpoint(
    repo_id="google/gemma-4-31B-it",
    huggingfacehub_api_token=os.getenv("HF_TOKEN"),
    max_new_tokens=4000,
)

model = ChatHuggingFace(llm=llm)
