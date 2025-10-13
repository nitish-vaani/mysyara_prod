import asyncio
import pickle
import uuid

import aiohttp
from dotenv import load_dotenv
from livekit.agents import tokenize
from livekit.plugins import openai, rag
from tqdm import tqdm
import os

load_dotenv(dotenv_path="/app/.env.local")
load_dotenv()

file_name = os.getenv("VECTOR_FILE_NAME", "knowledge-base-mysyara")
embeddings_dimension = int(os.getenv("EMBEDDINGS_DIMENSION", 1536))
raw_data_path = os.getenv("VECTOR_RAW_DATA_PATH", f"/app/rag/rag_knowledge_base/{file_name}.txt")
index_path = os.getenv("VECTOR_INDEX_PATH", "/app/rag/vdb_data")
pkl_path = os.getenv("VECTOR_DATA_PKL_PATH", f"/app/rag/rag_knowledge_base/{file_name}.pkl")
raw_data = open(raw_data_path, "r", encoding="utf-8").read()

# from this blog https://openai.com/index/new-embedding-models-and-api-updates/
# 512 seems to provide good MTEB score with text-embedding-3-small

async def _create_embeddings(
    input: str, http_session: aiohttp.ClientSession
) -> openai.EmbeddingData:
    results = await openai.create_embeddings(
        input=[input],
        model="text-embedding-3-small",
        dimensions=embeddings_dimension,
        http_session=http_session,
    )
    return results[0]


async def main() -> None:
    async with aiohttp.ClientSession() as http_session:
        idx_builder = rag.annoy.IndexBuilder(f=embeddings_dimension, metric="angular")

        paragraphs_by_uuid = {}
        for p in tokenize.basic.tokenize_paragraphs(raw_data):
            p_uuid = uuid.uuid4()
            paragraphs_by_uuid[p_uuid] = p

        for p_uuid, paragraph in tqdm(paragraphs_by_uuid.items()):
            resp = await _create_embeddings(paragraph, http_session)
            idx_builder.add_item(resp.embedding, p_uuid)

        idx_builder.build()
        idx_builder.save(index_path)
        print("saved index in VDB.")

        # save data with pickle
        with open(pkl_path, "wb") as f:
            pickle.dump(paragraphs_by_uuid, f)


if __name__ == "__main__":
    asyncio.run(main())
