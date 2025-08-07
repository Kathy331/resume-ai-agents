import os
import json

from typing import Dict, Any

from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from agents.resume_analyzer.config import STRUCTURED_SUMMARY_PROMPT
from agents.keyword_extractor.agent import KeywordExtractorAgent

from shared.llm_client import call_llm

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_unstructured import UnstructuredLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

class ResumeAnalyzerAgent(BaseAgent):
    """
    An agent that analyzes resumes by:
    1. Extracting and parsing text from supported resume files.
    2. Generating a structured summary using an LLM.
    3. Extracting relevant keywords (skills, roles, companies) using a sub-agent.
    """
    load_dotenv()

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Fallback to prompt constant if not provided via config
        self.prompt_template = config.get("prompt_template", STRUCTURED_SUMMARY_PROMPT)

        # Optional chunking behavior (default to safe, general values)
        self.chunk_size = config.get("chunk_size", 1500)
        self.chunk_overlap = config.get("chunk_overlap", 200)   

    def split_text(self, text: str, chunk_size: int = 1500, chunk_overlap: int = 200) -> list[str]:
        """
        Splits the resume text into smaller chunks to fit LLM token limits.

        Parameters
        ----------
        ext : str
            The full resume text.
        chunk_size : int
            Approximate number of characters per chunk (default 1500).
        chunk_overlap : int
            Overlap between chunks for contextual continuity.

        Returns
        -------
        List[str]
            List of resume text chunks.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        return [chunk.page_content for chunk in splitter.create_documents([text])]

    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extracts text from a resume file based on its extension.

        Parameters
        ----------
        file_path : str
            Path to the input resume file. Supported formats: .pdf, .txt, .docx

        Returns
        -------
        str
            Cleaned and concatenated text extracted from the resume.
        """
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_ext == ".txt":
            loader = TextLoader(file_path)
        elif file_ext == ".docx":
            loader = UnstructuredLoader(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        documents = loader.load()
        full_text = "\n\n".join([doc.page_content for doc in documents])
        return full_text

    async def generate_structured_summary(self, resume_text: str) -> dict:
        """
        Generates a structured summary of the resume text using an LLM.
        If the resume is too long, it is split into chunks and processed incrementally.

        Parameters
        ----------
        resume_text : str
            The full resume text.

        Returns
        -------
        dict
            Combined structured summary from all chunks.
        """
        try:
            chunks = self.split_text(resume_text)

            intermediate_summaries = []

            for i, chunk in enumerate(chunks):
                prompt = STRUCTURED_SUMMARY_PROMPT.format(text=chunk)
                response = await call_llm(prompt)
                parsed = json.loads(response)
                intermediate_summaries.append(parsed)

            # Return merged summaries as a list.
            return {"chunks": intermediate_summaries}

        except Exception as e:
            return {
                "error": f"Failed to extract structured summary: {str(e)}",
                "raw_response": response if 'response' in locals() else None
            }

    def validate_input(self, input_data: AgentInput) -> bool:
        """
        Validates that the required resume file path is present in the input.

        Parameters
        ----------
        input_data : AgentInput
            The input passed into the agent.

        Returns
        -------
        bool
            True if input is valid, False otherwise.
        """
        return "file_path" in input_data.data and isinstance(input_data.data["file_path"], str)

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Executes the resume analysis pipeline:
            1. Loads and parses resume text from a given file path.
            2. Generates a structured summary of resume content.
            3. Extracts keywords (skills, roles, companies) using a sub-agent.

        Parameters
        ----------
        input_data : AgentInput
            Contains a `file_path` key with the path to the resume file.

        Returns
        -------
        AgentOutput
            Structured analysis result, including summary, keywords, and metadata.
        """
        try:
            resume_path = input_data.data.get("file_path")
            if not resume_path:
                return AgentOutput(
                    success=False,
                    data={},
                    metadata={},
                    errors=["Missing resume file path in input_data.data"]
                )

            resume_text = self.extract_text_from_file(resume_path)
            structured_summary = await self.generate_structured_summary(resume_text)

            keyword_agent = KeywordExtractorAgent(config=self.config)
            keyword_input = AgentInput(data={"text": resume_text})
            keyword_result = await keyword_agent.execute(keyword_input)

            if keyword_result.success:
                structured_summary["extracted_keywords"] = keyword_result.data.get("keywords", "")
            else:
                structured_summary["extracted_keywords"] = ""
                structured_summary["keyword_extraction_error"] = keyword_result.errors

            return AgentOutput(
                success=True,
                data=structured_summary,
                metadata={"source_file": resume_path},
                errors=None
            )

        except Exception as e:
            return AgentOutput(
                success=False,
                data={},
                metadata={},
                errors=[str(e)]
            )