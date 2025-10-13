from rag.warm_up_rag import embeddings_dimension as EMBEDDINGS_DIMENSION
from livekit.plugins import openai, rag
from livekit.plugins import rag
import pickle
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="/app/.env.local")
# load_dotenv()



INDEX_PATH = os.getenv("VECTOR_INDEX_PATH", "/app/rag/vdb_data")
file_name = os.getenv("VECTOR_FILE_NAME", "knowledge-base-mysyara")
DATA_PATH = os.getenv("VECTOR_DATA_PKL_PATH", f"/app/rag/rag_knowledge_base/{file_name}.pkl")
with open(DATA_PATH, "rb") as f:
    paragraphs_by_uuid = pickle.load(f)    

async def enrich_with_rag(
    user_msg,
    top_k=5
) -> None:
    """
    Locate the last user message, use it to query the RAG model for
    the most relevant paragraph, add that to context, and generate a response.
    """
    annoy_index = rag.annoy.AnnoyIndex.load(INDEX_PATH)
    user_embedding = await openai.create_embeddings(
        input=[user_msg],
        model="text-embedding-3-small",
        dimensions=EMBEDDINGS_DIMENSION,
    )

    results = annoy_index.query(user_embedding[0].embedding, n=top_k)
    paragraphs = list()
    for res in results:
        paragraph = paragraphs_by_uuid[res.userdata]
        paragraphs.append(paragraph)

    return paragraphs
