import pytest
from agents.email_classifier.agent import EmailClassifierAgent
from agents.base_agent import AgentInput
from shared.google_oauth.google_email_functions import init_gmail_service, get_email_messages, get_email_message_details 
import os

## To run this test, ensure you have pytest installed and run `pytest tests/test_agents/test_email_classifier.py`
@pytest.mark.asyncio
async def test_email_classifier():
    agent = EmailClassifierAgent(config={})
    
    client_file = 'client_secret.json'
    service = init_gmail_service(client_file)

    messages = get_email_messages(service, folder_name='test', max_results=10)
    emails = []
    for msg in messages:
        details = get_email_message_details(service, msg['id'])
        if details:
            emails.append(details)
    input_data = AgentInput(data={"emails": emails, "user_email": "liveinthemoment780@gmail.com"})

    result = await agent.execute(input_data)
    assert result.success

    # Prepare output folder
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "test_email_classifier_output.txt")

    # Write input and output to the file
    with open(output_file, "w") as f:
        f.write("=== Email Classifier Test Result ===\n")
        f.write(f"Input Emails Count: {len(input_data.data['emails'])}\n\n")
        f.write("Classified Emails:\n")
        f.write(f"Interview: {result.data['interview']}\n")
        f.write(f"Personal: {result.data['personal']}\n")
        f.write(f"Other: {result.data['other']}\n")
        f.write("\nFull Result Object:\n")
        f.write(str(result.model_dump()))

    print(f"Email classifier test written to: {output_file}")