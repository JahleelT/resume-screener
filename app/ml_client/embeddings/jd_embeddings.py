from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def embed_chunks(chunks: list[Document], user_id: str) -> list[dict]:
  texts = [chunk.page_content for chunk in chunks]
  vectors = embeddings.embed_documents(texts)

  vector_data = []

  for (i, (vec, chunk)) in enumerate(zip(vectors, chunks)):
    jd_id = chunk.metadata.get("jd_id", "unknown")
    vector_id = f"{jd_id}_chunk{i}"

    vector_data.append(
      {
        "id": vector_id,
        "values": vec,
        "metadata": {
          "jd_id": jd_id,
          "user_id": user_id,
          "text": chunk.page_content,
          **chunk.metadata
        }
      }
    )

  return vector_data

def embed_query(query: str) -> list[float]:
  return embeddings.embed_documents([query])[0]