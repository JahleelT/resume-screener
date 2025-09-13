from pinecone import Pinecone, ServerlessSpec
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

if not pc.has_index("resume_screener"):
  pc.create_index(
    name="resume_screener",
    dimension=384,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
  )

index = pc.Index("resume_screener")

