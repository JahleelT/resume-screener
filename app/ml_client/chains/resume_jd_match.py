from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.schemas.resume_jd_match import ResumeJDMatch

parser = PydanticOutputParser(pydantic_object=ResumeJDMatch)

format_instructions = parser.get_format_instructions()

prompt = ChatPromptTemplate.from_template("""
You are an AI assistant that evaluates how well a candidate's resume matches a job description.

Job Description:
{job_description}

Candidate Resume:
{resume_text}

Instructions:
- Compare the resume to the job description.
- Identify overlapping skills, missing skills, and produce a summary.
- Provide a numeric match_score between 0 and 1.
- Return your result strictly following this JSON schema:
{format_instructions}
""")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chain = prompt | model | parser

def match_resume_to_jd(resume_text: str, jd_text: str) -> ResumeJDMatch:
  return chain.invoke({
    "job_description": jd_text,
    "resume_text": resume_text,
    "format_instructions": format_instructions,
  })