from langchain.embeddings import HuggingFaceBgeEmbeddings

def embed_chunks(chunks: list[Document]):
  embeddings = HuggingFaceBgeEmbeddings(model_name="all-MiniLM-L6-v2")

  texts = [chunk.page_content for chunk in chunks]
  vectors = embeddings.embed_documents(texts)

  vector_data = [
    {"vector": vec, "metadata": chunk.metadata}
    for vec, chunk in zip(vectors, chunks)
  ]

  return vector_data


