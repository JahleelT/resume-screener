from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.backend.schemas.writer_schema import WriterOutput

parser = PydanticOutputParser(pydantic_object = WriterOutput)

prompt = ChatPromptTemplate.from_messages([
  ("system", """You are a professional career advisor and report writer. Your task is to transform structured analysis data about a candidate's resume versus a job description into a clear, concise, and human-friendly report. 
  Maintain a professional and approachable tone. 
  Do not add new facts; only reframe the information provided. 
  Ensure the report is easy to read for recruiters and candidates, with actionable recommendations and a clear overall rating.
  """),

  ("user", """Using the structured analysis data below, produce a polished, human-readable report. 
  The report should be easy for both recruiters and candidates to understand. 
  Include the following sections:

  1. A 3-5 sentence summary of the candidate's fit for the role.
  2. Actionable recommendations for improving the resume.
  3. An overall rating, e.g., "Strong Match", "Moderate Match", or "Weak Match".

  Analysis Data:
  {analysis_result}

  {format_instructions}
  """)
]).partial(format_instructions = parser.get_format_instructions())

llm = ChatOpenAI(model = "gpt-4o-mini", temperature = 0)

def get_written_human_output(analysis_result: str) -> WriterOutput:
  return (prompt | llm | parser).invoke({"analysis_result": analysis_result})