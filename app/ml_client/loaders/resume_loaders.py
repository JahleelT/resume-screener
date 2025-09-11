from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import TextLoader

def load_resume(file_path: str):
  if file_path.endswith(".pdf"):
    loader = UnstructuredPDFLoader(file_path)

    docs = loader.load()

    docs[0]

    # TODO check doc and split into chunks
    
  elif file_path.endswith(".docx"):
    loader = UnstructuredWordDocumentLoader(file_path)

    docs = loader.load()

    docs[0]

    # TODO use UnstructuredWordDocumentLoader here

  elif file_path.endswith(".txt"):
    loader = TextLoader(file_path)

    docs = loader.load()

    docs[0]

    # TODO use TextLoader here
