from agents.base_agent import BaseAgent, AgentInput, AgentOutput

class EmailClassifierAgent(BaseAgent):
    def validate_input(self, input_data: AgentInput) -> bool:
        # Expecting a list of emails in input_data.data["emails"]
        return (
            "emails" in input_data.data and
            isinstance(input_data.data["emails"], list) and
            len(input_data.data["emails"]) > 0
        )

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        emails = input_data.data["emails"]
        user_email = input_data.data.get("user_email", "").lower()

        interview_ids = []
        personal_ids = []
        other_ids = []

        for email in emails:
            subject = email.get("subject", "").lower()
            body = email.get("body", "").lower()
            sender = email.get("from", "").lower()
            recipients = [r.lower() for r in email.get("to", [])]

            # Classify as "interview" if subject/body contains interview keywords
            if any(keyword in subject or keyword in body for keyword in [
                "interview", "recruiter", "interview invitation", "interview schedule", 
                "interview confirmation", "interview details", "interview request",
                "interview time", "interview date", "interview location", "interview link",
                "interview call", "interview meeting", "interview session", "screening",
                "hiring manager", "recruiter call", "talent acquisition", "onsite interview",
                "virtual interview", "phone interview", "video interview", "technical interview",
                "behavioral interview"
            ]):
                interview_ids.append(email["id"])
            # Classify as "personal" if user is the sender
            elif user_email and sender == user_email:
                personal_ids.append(email["id"])
            else:
                other_ids.append(email["id"])

        return AgentOutput(
            success=True,
            data={
                "interview": interview_ids,
                "personal": personal_ids,
                "other": other_ids
            },
            metadata={},
            errors=None
        )