from langchain.embeddings import HuggingFaceBgeEmbeddings


embeddings = HuggingFaceBgeEmbeddings(model_name="all-MiniLM-L6-v2")

def embed_chunks(chunks: list[Document]):
  texts = [chunk.page_content for chunk in chunks]
  vectors = embeddings.embed_documents(texts)

  vector_data = []
  
  for (i, (vec, chunk)) in enumerate(zip(vectors, chunks)):
    resume_id = chunk.metadata.get("resume_id", "unknown")
    vector_id = f"{resume_id}_chunk{i}"

    vector_data.append(
      {
        "id": vector_id,
        "values": vec,
        "metadata": chunk.metadata
      }
    )

  return vector_data


