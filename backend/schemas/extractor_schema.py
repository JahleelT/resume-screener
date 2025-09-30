from pydantic import BaseModel, Field
from typing import List

class ExtractedResume(BaseModel):
  name: str = Field(..., description = "Full name of the candidate if present, otherwise empty string")
  skills: List[str] = Field(..., description = "List of skills explicitly mentioned in the resume")
  experiences: List[str] = Field(..., description = "List of professional experiences (titles, companies, roles, or descriptions)")
  education: List[str] = Field(..., description = "Educational background items such as degree, school, or major")
  certifications: List[str] = Field(..., description = "Professional certifications or licenses")
  summary: str = Field(..., description = "1-2 sentence summary of the candidate's background")