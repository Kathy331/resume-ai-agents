import pytest
from agents.resume_analyzer.agent import ResumeAnalyzerAgent
from agents.base_agent import AgentInput
import json
import os

@pytest.mark.asyncio
async def test_generate_structured_summary():
    agent = ResumeAnalyzerAgent(config={})

    sample_resume = """
    John Doe
    Email: john.doe@email.com
    Phone: (555) 123-4567

    Summary:
    Experienced software engineer with expertise in Python, cloud infrastructure, and distributed systems.

    Experience:
    Senior Software Engineer at OpenAI (2021 - Present)
    - Built scalable ML systems
    - Led team of 4 engineers

    Software Engineer at Google (2018 - 2021)
    - Worked on Gmail backend
    - Improved system latency by 30%

    Education:
    B.S. in Computer Science, MIT, 2014 - 2018

    Certifications:
    AWS Certified Solutions Architect

    Skills:
    Python, Kubernetes, GCP, Docker
    """

    result = await agent.generate_structured_summary(sample_resume)

    # Save results for inspection
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "test_resume_summary_output.json")

    with open(output_file, "w") as f:
        import json
        json.dump(result, f, indent=2)

    # Basic sanity checks
    assert isinstance(result, dict)
    assert "chunks" in result, "Expected 'chunks' key in structured summary"
    assert isinstance(result["chunks"], list), "'chunks' should be a list"

    # Check for desired content inside chunks
    chunk_data = result.get("chunks", [])
    assert any(
        "skills" in chunk or "summary" in chunk or "experience" in chunk
        for chunk in chunk_data
    ), "Expected keys not found in any chunk of the structured summary."

    print(f"Resume summary output saved to: {output_file}")

# ==> Temp test TODO: delete
# @pytest.mark.asyncio
# async def test_load_resume_text():
#     agent = ResumeAnalyzerAgent(config={})

#     # Ensure file path exists
#     test_file_path = "tests/sample_data/sample_resume.txt"
#     assert os.path.exists(test_file_path), f"Test file not found: {test_file_path}"

#      # Prepare input data 
#     input_data = AgentInput(data={"file_path": test_file_path})
#     # Execute the agent
#     result = await agent.execute(input_data)

#     assert result.success, f"Agent failed with errors: {result.errors}"
#     assert "raw_resume_text" in result.data
#     assert len(result.data["raw_resume_text"]) > 20  # Arbitrary length check

#     # Save result to outputs folder for inspection
#     output_dir = "outputs"
#     os.makedirs(output_dir, exist_ok=True)
#     output_file = os.path.join(output_dir, "test_resume_text_output.txt")

#     with open(output_file, "w") as f:
#         f.write("=== Resume Text Load Test ===\n")
#         f.write(f"Source File: {test_file_path}\n\n")
#         f.write(f"Extracted Text:\n{result.data['raw_resume_text']}\n")
#         f.write("\nFull Result Object:\n")
#         f.write(str(result.model_dump()))

#     print(f"Test output written to: {output_file}")

@pytest.mark.asyncio
async def test_resume_analyzer_with_keywords():
    """
    This test 
    """
    # Instantiate the resume analyzer
    agent = ResumeAnalyzerAgent(config={})
            
    # Ensure file path exists
    test_file_path = "tests/sample_data/sample_resume.txt"
    assert os.path.exists(test_file_path), f"Test file not found: {test_file_path}"

    # Prepare input data
    input_data = AgentInput(data={"file_path": test_file_path})

    # Execute the agent
    result = await agent.execute(input_data)

    # Assertions
    assert result.success, f"Agent execution failed: {result.errors}"
    assert "extracted_keywords" in result.data, "Keywords missing from structured output"
    assert isinstance(result.data["extracted_keywords"], str), "Keywords should be a string"
    assert len(result.data["extracted_keywords"]) > 0, "Extracted keywords should not be empty"

    # Save output for review
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/test_resume_with_keywords_output.json"
    with open(output_path, "w") as f:
        json.dump(result.model_dump(), f, indent=2)

    print(f"Resume + keyword test output saved to: {output_path}")

@pytest.mark.asyncio
async def test_pdf_resume_analysis():
    agent = ResumeAnalyzerAgent(config={})
    test_file_path = "tests/sample_data/sample_resume.pdf"
    assert os.path.exists(test_file_path), f"PDF resume not found: {test_file_path}"

    input_data = AgentInput(data={"file_path": test_file_path})
    result = await agent.execute(input_data)

    assert result.success, f"PDF analysis failed: {result.errors}"
    assert "chunks" in result.data
    assert any("name" in chunk for chunk in result.data["chunks"]), "No name found in chunks"
    assert any("skills" in chunk for chunk in result.data["chunks"]), "No skills found in chunks"
    assert any("summary" in chunk for chunk in result.data["chunks"]), "No summary found in chunks"
    assert any("education" in chunk for chunk in result.data["chunks"]), "No education found in chunks"
    assert "extracted_keywords" in result.data

    # Save output for review
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/test_resume_with_keywords_output_2.json"
    with open(output_path, "w") as f:
        json.dump(result.model_dump(), f, indent=2)

    print(f"Resume + keyword test output saved to: {output_path}")

@pytest.mark.asyncio
async def test_docx_resume_analysis():
    agent = ResumeAnalyzerAgent(config={})
    test_file_path = "tests/sample_data/sample_resume.docx"
    assert os.path.exists(test_file_path), f"DOCX resume not found: {test_file_path}"

    input_data = AgentInput(data={"file_path": test_file_path})
    result = await agent.execute(input_data)

    assert result.success, f"DOCX analysis failed: {result.errors}"
    assert "chunks" in result.data
    assert any("name" in chunk for chunk in result.data["chunks"]), "No name found in chunks"
    assert any("skills" in chunk for chunk in result.data["chunks"]), "No skills found in chunks"
    assert any("summary" in chunk for chunk in result.data["chunks"]), "No summary found in chunks"
    assert any("education" in chunk for chunk in result.data["chunks"]), "No education found in chunks"
    assert "extracted_keywords" in result.data

    # Save output for review
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/test_resume_with_keywords_output_3.json"
    with open(output_path, "w") as f:
        json.dump(result.model_dump(), f, indent=2)

    print(f"Resume + keyword test output saved to: {output_path}")