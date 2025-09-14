from pinecone import Index
from app.ml_client.embeddings import jd_embeddings

def upsert_vectors(index: Index, vector_data: list[dict]) -> None:
  jd_id = vector_data[0]["metadata"]["jd_id"]
  user_id = vector_data[0]["metadata"]["user_id"]
  meta_filter = {"jd_id": jd_id, "user_id":user_id}

  vectors_exist = query_jd_exists(index, meta_filter)

  if not vectors_exist:
    index.upsert(vectors=vector_data)


def delete_vectors_by_jd(index: Index, meta_filter: dict) -> None:
  required_keys = {"jd_id", "user_id"}

  if set(meta_filter.keys()) != required_keys:
    raise ValueError(f"Filter must only contain {required_keys}")

  pinecone_filter = {
    "jd_id": {"$eq": meta_filter["jd_id"]},
    "user_id": {"$eq": meta_filter["user_id"]}
  }

  index.delete(
    filter = pinecone_filter
  )

def query_vectors(index: Index, query: str, user_id: str) -> list[dict]:
  embedded_query = jd_embeddings.embed_query(query)

  results = index.query(
    vector = embedded_query,
    top_k = 10,
    filter = {
      "user_id": {"$eq": user_id},
    },
    include_metadata= True
  )

  return results["matches"]

def query_jd_exists(index: Index, meta_filter: dict) -> bool:

  required_keys = {"jd_id", "user_id"}

  if set(meta_filter.keys()) != required_keys:
    raise ValueError(f"Filter must only contain {required_keys}")

  results = index.query(
    top_k = 1,
    include_values = False,
    filter = meta_filter
  )

  return len(results["matches"]) > 0





  