import re
from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentInput, AgentOutput
import spacy

# Technologies used for entity extraction:
# - Regex: Finds exact text patterns, fast but breaks if text changes.
# - spaCy NER: ML model to find names, dates, companies in natural text

class EntityExtractor(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.nlp = spacy.load("en_core_web_sm")

    def validate_input(self, input_data: AgentInput) -> bool:
        return "text" in input_data.data and bool(input_data.data["text"].strip())

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        text = input_data.data.get("text", "")
        try:
            company_regex = self.extract_company_regex(text)
            role_regex = self.extract_role_regex(text)
            datetime_regex = self.extract_datetime_regex(text)
            interviewer_regex = self.extract_interviewer_regex(text)

            doc = self.nlp(text)
            company_ner = self.extract_company_ner(doc)
            role_heuristic = self.extract_role_heuristic(text)
            datetime_ner = self.extract_datetime_ner(doc)
            interviewer_ner = self.extract_interviewer_ner(doc)

            company = company_regex or company_ner or ""
            role = role_regex or role_heuristic or ""
            interview_datetime = datetime_regex or datetime_ner or ""
            interviewer = interviewer_regex or interviewer_ner or ""

            return AgentOutput(
                success=True,
                data={
                    "company": company,
                    "role": role,
                    "interview_datetime": interview_datetime,
                    "interviewer": interviewer,
                },
                metadata={},
                errors=None
            )
        except Exception as e:
            return AgentOutput(
                success=False,
                data={},
                metadata={},
                errors=[str(e)]
            )

    def extract_company_regex(self, text: str) -> str:
        match = re.search(r"(?:at|with)\s+([A-Z][\w&.\- ]+)", text)
        return match.group(1).strip() if match else ""

    def extract_role_regex(self, text: str) -> str:
        match = re.search(r"interview for the position of\s+([A-Z][\w\s]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def extract_datetime_regex(self, text: str) -> str:
        match = re.search(
            r"(?:on|at|when:)\s+([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)",
            text,
            re.IGNORECASE,
        )
        return match.group(1).strip() if match else ""

    def extract_interviewer_regex(self, text: str) -> str:
        match = re.search(r"(?:Interview(er)?[:\-]?\s*|Interview with\s+)([A-Z][a-z]+\s+[A-Z][a-z]+)", text)
        return match.group(2).strip() if match else ""

    def extract_company_ner(self, doc) -> str:
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text
        return ""

    def extract_datetime_ner(self, doc) -> str:
        for ent in doc.ents:
            if ent.label_ in ("DATE", "TIME"):
                return ent.text
        return ""

    def extract_interviewer_ner(self, doc) -> str:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if re.search(r"(Interviewer|Interview with)", doc.text):
                    return ent.text
        return ""

    def extract_role_heuristic(self, text: str) -> str:
        match = re.search(r"(?:position of|role as)\s+([A-Z][\w\s]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else ""
