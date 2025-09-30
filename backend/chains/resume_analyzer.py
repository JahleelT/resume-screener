from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from backend.schemas.analyzer_schema import AnalysisResult

parser = PydanticOutputParser(pydantic_object = AnalysisResult)

prompt = ChatPromptTemplate.from_messages([
  ("system", """You are an expert career evaluator. Your task is to compare a candidate's extracted resume data with a job description and provide a structured analysis. 
  Use only information explicitly present in the resume and JD. Do not invent or infer details. 
  Strictly follow the output schema and provide objective scores, matched/missing skills, strengths, and weaknesses.
  """),

  ("user", """Compare the candidate's extracted resume information with the job description. Provide a structured analysis including: match_score, matched_skills, missing_skills, strengths, and weaknesses. 
  Only use information present in the provided data; do not infer new details.

  Candidate Resume (extracted_info):
  {resume_info}

  Job Description:
  {jd_text}

  {format_instructions}
  """),
]).partial(format_instructions=parser.get_format_instructions())

llm = ChatOpenAI(model = "gpt-4o-mini", temperature = 0)

def get_analysis_result_chain(resume_info: str, jd_text: str) -> AnalysisResult:
  return (prompt | llm | parser).invoke({"resume_info": resume_info, "jd_text": jd_text})