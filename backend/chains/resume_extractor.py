from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from backend.schemas.extractor_schema import ExtractedResume

parser = PydanticOutputParser(pydantic_object = ExtractedResume)

prompt = ChatPromptTemplate.from_messages([
  ("system", """You are a precise information extractor that pulls structured data from resumes. Always extract the candidate's name, skills, experiences, education, certifications, and a brief summary of their background. 
  Do not add information that is not present in the resume. 
  Return output strictly in the structured format provided."""),
  
  ("user", """Extract the requested structured information from the resume text below. 
  Ensure all fields (name, skills, experiences, education, certifications, summary) are filled accurately using only the information in the resume.

  Resume text:
  {resume_text}

  {format_instructions}"""),
  ]).partial(format_instructions=parser.get_format_instructions())

llm = ChatOpenAI(model = "gpt-4o-mini", temperature = 0)

def get_resume_extractor_chain(resume_text: str) -> ExtractedResume:
  return (prompt | llm | parser).invoke({"resume_text": resume_text})