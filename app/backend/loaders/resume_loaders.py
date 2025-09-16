from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_resume(file_path: str) -> list[Document]:
  if file_path.endswith(".pdf"):
    loader = UnstructuredPDFLoader(file_path)

    
  elif file_path.endswith(".docx"):
    loader = UnstructuredWordDocumentLoader(file_path)

  elif file_path.endswith(".txt"):
    loader = TextLoader(file_path)

  docs = loader.load()
  return docs



def split_resume(loaded_resume: list[Document]) -> list[Document]:
  splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
  )

  chunks = splitter.split_documents(loaded_resume)
  return chunks
