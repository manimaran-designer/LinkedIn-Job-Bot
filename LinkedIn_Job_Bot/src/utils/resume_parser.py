from models.schemas import ResumeData

async def parse_resume(file_path: str) -> str:
    """Mock extractor for extracting text from PDF/DOC resume."""
    with open(file_path, 'r') as f:
        return f.read()

async def extract_resume_data(raw_text: str) -> ResumeData:
    """Mock parser to extract structured ResumeData from raw text."""
    # In a real app, you'd use LLM/Regex to parse out specific fields.
    # Here, we return dummy values corresponding to our mock text file.
    return ResumeData(
        skills=["Python", "PyTorch", "LangChain", "OpenRouter", "AWS", "SQL"],
        roles=["Software Engineer"],
        experience_level="Mid-Level",
        education="B.S. Computer Science",
        full_text=raw_text,
        location="Remote",
        years_experience=3
    )
