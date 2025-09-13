from pinecone_init import pc
from pinecone import Index
from app.ml_client.embeddings import resume_embeddings

def upsert_vectors(index: Index, vector_data: list[dict]) -> None:
  resume_id = vector_data[0]["metadata"]["resume_id"]
  user_id = vector_data[0]["metadata"]["user_id"]
  meta_filter = {"resume_id": resume_id, "user_id": user_id}

  vectors_exist = query_resume_exists(index, meta_filter)

  if not vectors_exist:
    index.upsert(vectors=vector_data)



def delete_vectors_by_resume(index: Index, meta_filter: dict) -> None:
  required_keys = {"resume_id", "user_id"}

  # Ensuring that the filter is only comprised of resume_id and user_id keys/values
  if set(meta_filter.keys()) != required_keys:
    raise ValueError(f"Filter must only contain {required_keys}")

  pinecone_filter = {
    "resume_id": {"$eq": meta_filter["resume_id"]},
    "user_id": {"$eq": meta_filter["user_id"]}
  }

  index.delete(
    filter = pinecone_filter
  )


def query_vectors(index: Index, query: str, user_id: str) -> list[dict]:
  embedded_query = resume_embeddings.embed_query(query)

  results = index.query(
    vector = embedded_query,
    top_k = 10,
    filter = { "user_id": {"$eq": user_id}},
    include_metadata = True
  )

  return results["matches"]


def query_resume_exists(index: Index, meta_filter: dict) -> bool:

  required_keys = {"resume_id", "user_id"}

  # Ensuring that the filter is only comprised of resume_id and user_id keys/values
  if set(meta_filter.keys()) != required_keys:
    raise ValueError(f"Filter must only contain {required_keys}")

  results = index.query(
    top_k = 1,
    include_values = False,
    filter = meta_filter
  )
  
  return len(results["matches"]) > 0

