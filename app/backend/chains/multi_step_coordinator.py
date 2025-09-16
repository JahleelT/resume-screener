from resume_extractor import get_resume_extractor_chain
from resume_analyzer import get_analysis_result_chain
from resume_writer import get_written_human_output

def run_resume_pipeline(resume_text: str, jd_text: str, store_intermediate: bool = False, store_all: bool = True):
  extraction = get_resume_extractor_chain(resume_text)
  analyzed = get_analysis_result_chain(extraction, jd_text)
  human_ready = get_written_human_output(analyzed)

  if not store_intermediate:
    return human_ready.dict()
  
  if store_all:
    return {
      "extracted": extraction.dict(),
      "analysis": analyzed.dict(),
      "written": human_ready.dict()
    }
  else:
    return {
      "written": human_ready.dict()
    }