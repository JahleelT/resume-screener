from pinecone import Pinecone, ServerlessSpec
from pinecone import Index
from dotenv import load_dotenv
from pathlib import Path
import os

# retrieve the api_key and construct an instance of Pinecone

env_path = Path(__file__).resolve().parents[2] / ".env" # go up from current (embeddings) --> backend root (ml_client) --> app root (app)
load_dotenv(dotenv_path=env_path)

pinecone_key = os.getenv("PINECONE_API_KEY")

if not pinecone_key:
  raise ValueError("PINECONE_API_KEY not found. Did you load your .env?")


pc = Pinecone(api_key=pinecone_key)


# Now connect to the index

def begin_index(index_name: str) -> Index:
  if not pc.has_index(index_name):
    pc.create_index(
      name=index_name,
      dimension=384,
      metric="cosine",
      spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

  index = pc.Index(index_name)

  while not pc.describe_index(index_name).status.ready:
    time.sleep(1)

  return index


