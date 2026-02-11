# app/ai/ingestion/parser.py
"""
CV Parser - Extract Structured Data from CVs using Mistral OCR + LLM

OWNERS: Amina & Balsam
STATUS: Integrated into TalentGrid

This module handles:
1. Reading PDF files using Mistral OCR
2. Extracting structured data using LLM (Groq primary, Gemini fallback)
3. Returning structured data matching the Candidate model schema

Dependencies:
- pip install mistralai groq langchain-google-genai python-docx
"""

import base64
import json
import os
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy-loaded clients and chains
_mistral_client = None
_groq_client = None
_cv_chain = None

# Shared prompt for CV parsing (used by both Groq and Gemini)
CV_PARSING_PROMPT = """You are an expert CV parser.

Your task:
Convert the following raw CV text into a STRICT JSON object
that EXACTLY follows the schema below.

Rules:
- Output JSON only. No explanations. No markdown.
- If a field is missing, use null or empty list.
- experience_years must be an integer.
- Dates must be "YYYY" or "YYYY-MM" or "present".
- Do NOT add extra fields.
- links must be a JSON object (key-value).

Schema:
{{
  "name": "required",
  "email": null,
  "phone": null,
  "title": null,
  "location": null,
  "experience_years": 0,
  "summary": null,
  "skills": [],
  "languages": [
    {{
      "name": "",
      "level": ""
    }}
  ],
  "education": [
    {{
      "degree": "",
      "field": "",
      "institution": "",
      "from": "",
      "to": ""
    }}
  ],
  "experience": [
    {{
      "role": "",
      "organization": "",
      "from": "",
      "to": "",
      "description": ""
    }}
  ],
  "certifications": [],
  "projects_or_work": [],
  "links": {{}}
}}

CV TEXT:
{cv_text}"""


def _get_mistral_client():
    """Lazy load Mistral client."""
    global _mistral_client
    if _mistral_client is None:
        try:
            from mistralai import Mistral
            api_key = os.getenv("MISTRAL_API_KEY", "")
            if not api_key:
                # Try loading from app config
                try:
                    from app.config import settings
                    api_key = settings.MISTRAL_API_KEY
                except:
                    pass
            if not api_key:
                raise ValueError("MISTRAL_API_KEY not set")
            _mistral_client = Mistral(api_key=api_key)
            logger.info("Mistral client initialized")
        except ImportError:
            raise ImportError("mistralai is not installed. Run: pip install mistralai")
    return _mistral_client


def _get_groq_client():
    """Lazy load Groq client (primary LLM provider - free tier with 14,400 req/day)."""
    global _groq_client
    if _groq_client is None:
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY", "")
            if not api_key:
                try:
                    from app.config import settings
                    api_key = settings.GROQ_API_KEY
                except:
                    pass
            if api_key:
                _groq_client = Groq(api_key=api_key)
                logger.info("Groq client initialized (primary LLM)")
            else:
                logger.warning("GROQ_API_KEY not set - will use Gemini as primary")
                return None
        except ImportError:
            logger.warning("groq package not installed. Run: pip install groq")
            return None
    return _groq_client


def _get_cv_chain():
    """Lazy load Google Gemini chain (fallback LLM)."""
    global _cv_chain
    if _cv_chain is None:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            # Get API key from environment or config
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
            if not api_key:
                try:
                    from app.config import settings
                    api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
                except:
                    pass

            if api_key:
                os.environ["GOOGLE_API_KEY"] = api_key

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.1
            )

            cv_prompt = ChatPromptTemplate.from_template(CV_PARSING_PROMPT)
            _cv_chain = cv_prompt | llm | StrOutputParser()
            logger.info("Gemini CV chain initialized (fallback LLM)")

        except ImportError as e:
            raise ImportError(
                f"Required packages not installed. Run: pip install langchain-google-genai\nError: {e}"
            )
    return _cv_chain


def _parse_with_groq(cv_text: str) -> dict:
    """
    Parse CV text using Groq (Llama 3.1 70B).

    Groq offers 14,400 requests/day free - much more than Gemini's ~1,500.
    """
    client = _get_groq_client()
    if client is None:
        return {"error": "Groq client not available"}

    try:
        prompt = CV_PARSING_PROMPT.format(cv_text=cv_text)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Current best free model (successor to 3.1)
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4096
        )

        result = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if result.startswith("```"):
            lines = result.splitlines()
            result = "\n".join(lines[1:-1]).strip()

        logger.info("CV parsed successfully with Groq (Llama 3.3 70B)")
        return json.loads(result)

    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse Groq JSON: {str(e)}", "raw": result}
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Groq parsing failed: {error_msg}")
        return {"error": f"Groq API error: {error_msg}"}


def _pdf_to_base64(pdf_path: str) -> str:
    """Convert PDF file to base64 string."""
    with open(pdf_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def mistral_ocr_return(pdf_path: str) -> dict:
    """
    Process PDF using Mistral OCR to extract text.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with pages containing extracted content
    """
    from mistralai.models import DocumentURLChunk

    client = _get_mistral_client()
    encoded_pdf = _pdf_to_base64(pdf_path)
    data_url = f"data:application/pdf;base64,{encoded_pdf}"

    response = client.ocr.process(
        document=DocumentURLChunk(document_url=data_url),
        model="mistral-ocr-latest"
    )

    response_dict = json.loads(response.model_dump_json())

    pages_by_index = {}
    for page in response_dict.get("pages", []):
        idx = page.get("index")
        content = page.get("content") or page.get("markdown") or ""
        if idx is not None:
            pages_by_index[idx] = content

    final_pages = [{"index": idx, "content": content} for idx, content in sorted(pages_by_index.items())]

    logger.info(f"[Mistral OCR] Processed: {Path(pdf_path).name}")

    return {"pages": final_pages}


def _parse_with_gemini(cv_text: str) -> dict:
    """
    Parse CV text using Gemini (fallback LLM).
    """
    try:
        cv_chain = _get_cv_chain()
        response = cv_chain.invoke({"cv_text": cv_text}).strip()

        if not response:
            return {"error": "Gemini returned empty response"}

        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.splitlines()
            response = "\n".join(lines[1:-1]).strip()

        logger.info("CV parsed successfully with Gemini")
        return json.loads(response)

    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse Gemini JSON: {str(e)}", "raw": response}
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Gemini parsing failed: {error_msg}")
        return {"error": f"Gemini API error: {error_msg}"}


def gemini_structured_cv_return(mistral_ocr_output: dict) -> dict:
    """
    Extract structured CV data from OCR output using LLM.

    Strategy: Try Groq first (14,400 req/day free), fall back to Gemini.

    Args:
        mistral_ocr_output: Output from mistral_ocr_return

    Returns:
        Structured CV data as dictionary
    """
    pages = mistral_ocr_output.get("pages", [])
    cv_text = "\n".join([p.get("content", "") for p in pages]).strip()

    if not cv_text:
        return {"error": "CV text is empty after OCR"}

    # Strategy: Groq first (free, fast, high limit), Gemini as fallback
    # 1. Try Groq (Llama 3.1 70B) - 14,400 requests/day free
    groq_result = _parse_with_groq(cv_text)
    if "error" not in groq_result:
        return groq_result

    logger.info(f"Groq failed, trying Gemini as fallback. Groq error: {groq_result.get('error')}")

    # 2. Fallback to Gemini
    gemini_result = _parse_with_gemini(cv_text)
    if "error" not in gemini_result:
        return gemini_result

    # Both failed - return the error
    return {"error": f"All LLM providers failed. Groq: {groq_result.get('error')}. Gemini: {gemini_result.get('error')}"}


def _extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except ImportError:
        raise ValueError("python-docx not installed. Run: pip install python-docx")


async def parse_cv(file_path: str) -> Dict[str, Any]:
    """
    Parse a CV file (PDF or DOCX) and extract structured information.

    This is the main entry point for CV parsing in TalentGrid.

    Args:
        file_path: Absolute path to the CV file

    Returns:
        Dictionary with extracted candidate information matching the Candidate model.

    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If file doesn't exist
        ImportError: If required dependencies are not installed
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CV file not found: {file_path}")

    # Determine file type
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        # Use Mistral OCR for PDF
        ocr_result = mistral_ocr_return(file_path)
        pages = ocr_result.get("pages", [])
        raw_text = "\n".join([p.get("content", "") for p in pages])

        # Parse with Gemini
        parsed_data = gemini_structured_cv_return(ocr_result)

    elif file_extension in ['.docx', '.doc']:
        # For DOCX, extract text directly
        raw_text = _extract_text_from_docx(file_path)

        # Create OCR-like structure for Gemini
        ocr_result = {"pages": [{"index": 0, "content": raw_text}]}
        parsed_data = gemini_structured_cv_return(ocr_result)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Use PDF or DOCX.")

    if not raw_text.strip():
        raise ValueError("Could not extract text from CV file")

    if "error" in parsed_data:
        raise ValueError(f"CV parsing failed: {parsed_data['error']}")

    # Return data matching the Candidate model schema
    return {
        # Basic info
        "name": parsed_data.get("name", "Unknown"),
        "email": parsed_data.get("email"),
        "phone": parsed_data.get("phone"),
        "title": parsed_data.get("title"),
        "location": parsed_data.get("location"),
        "years_experience": parsed_data.get("experience_years", 0),
        "summary": parsed_data.get("summary"),

        # Arrays
        "skills": parsed_data.get("skills", []),
        "languages": parsed_data.get("languages", []),
        "certifications": parsed_data.get("certifications", []),
        "projects": parsed_data.get("projects_or_work", []),

        # Complex JSONB fields
        "education": parsed_data.get("education", []),
        "experience": parsed_data.get("experience", []),
        "links": parsed_data.get("links", {}),

        # Raw text for reference
        "raw_text": raw_text,
    }
