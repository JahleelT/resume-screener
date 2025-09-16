from app.backend.embeddings.resume_embeddings import embed_query
from app.backend.utils.pinecone_res_utils import query_resume_chunks_for_jd
from app.backend.chains.resume_jd_match import match_resume_to_jd
from pinecone import Index

def match_resume_with_retrieval(index: Index, resume_id: str, jd_text: str, top_k: int = 5):
  chunks = query_resume_chunks_for_jd(index, resume_id, jd_text, top_k)

  resume_text = " ".join([c["text"] for c in chunks])

  return match_resume_to_jd(resume_text, jd_text)