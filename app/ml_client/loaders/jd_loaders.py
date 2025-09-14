from langchain_community.document_loaders import PlaywrightURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
  try:
    result = urlparse(url)
    return all([result.scheme in ("http", "https"), result.netloc])
  except:
    return False

def load_jd(url: str) -> list[Document]:
  if not is_valid_url(url):
    raise ValueError(f"Invalid URL: {url}")

  loader = PlaywrightURLLoader([url])
  
  docs = loader.load()
  return docs

def split_jd(loaded_jd: list[Document]) -> list[Document]:
  splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
  )

  chunks = splitter.split_documents(loaded_jd)
  return chunks