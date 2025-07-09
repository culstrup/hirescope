"""
Shared pytest fixtures and configuration
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Get the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_path():
    """Return the path to the fixtures directory"""
    return FIXTURES_DIR


@pytest.fixture
def load_fixture():
    """Factory fixture to load JSON fixtures"""

    def _load_fixture(filename):
        filepath = FIXTURES_DIR / filename
        with open(filepath) as f:
            return json.load(f)

    return _load_fixture


@pytest.fixture
def mock_greenhouse_client():
    """Mock GreenhouseClient for testing"""
    with patch("hirescope.greenhouse_api.GreenhouseClient") as mock:
        client = Mock()

        # Load mock data
        with open(FIXTURES_DIR / "api_responses" / "greenhouse_jobs.json") as f:
            jobs_data = json.load(f)
        with open(FIXTURES_DIR / "api_responses" / "greenhouse_candidates.json") as f:
            candidates_data = json.load(f)

        # Configure mock methods
        client.get_jobs.return_value = jobs_data["jobs"]
        client.get_job.return_value = jobs_data["jobs"][0]
        client.get_candidates.return_value = candidates_data["123456"]

        mock.return_value = client
        yield client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch("openai.OpenAI") as mock:
        client = Mock()

        # Load mock responses
        with open(FIXTURES_DIR / "api_responses" / "openai_scoring.json") as f:
            responses = json.load(f)

        # Configure mock to return different responses
        client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content=json.dumps(responses[0])))]),
            Mock(choices=[Mock(message=Mock(content=json.dumps(responses[1])))]),
        ]

        mock.return_value = client
        yield client


@pytest.fixture
def sample_pdf_content():
    """Mock PDF content for testing"""
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R >>
endobj
"""


@pytest.fixture
def sample_docx_content():
    """Mock DOCX content for testing"""
    # This is a simplified representation
    # In real tests, you might want to use a proper DOCX structure
    return b"PK\x03\x04"  # DOCX files start with ZIP header


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """John Doe
Software Engineer
john.doe@example.com | (555) 123-4567

EXPERIENCE
Senior Software Engineer - TechCorp (2020-Present)
• Led development of microservices architecture
• Reduced API response times by 40%
• Mentored team of 5 junior developers

Software Engineer - StartupXYZ (2017-2020)
• Built RESTful APIs using Python and Flask
• Implemented CI/CD pipeline with Jenkins
• Developed React-based frontend components

EDUCATION
BS Computer Science - State University (2017)

SKILLS
Languages: Python, JavaScript, Java
Frameworks: Django, Flask, React, Node.js
Tools: Docker, Kubernetes, AWS, Git
"""


@pytest.fixture
def sample_cover_letter_text():
    """Sample cover letter text for testing"""
    return """Dear Hiring Manager,

I am writing to express my strong interest in the Senior Software Engineer position at your company. With over 8 years of experience in software development and a proven track record of delivering scalable solutions, I am confident I would be a valuable addition to your team.

In my current role at TechCorp, I have led the transformation of our monolithic architecture to microservices, resulting in improved scalability and reduced deployment times. I am particularly excited about your company's focus on innovation and would love to contribute to your mission.

Thank you for considering my application. I look forward to discussing how my skills and experience align with your needs.

Best regards,
John Doe
"""


@pytest.fixture
def temp_env_vars(monkeypatch):
    """Temporarily set environment variables for testing"""

    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)

    return _set_env


@pytest.fixture(autouse=True)
def reset_singleton_instances():
    """Reset any singleton instances between tests"""
    # This is useful if any of your classes use singleton pattern
    yield
    # Cleanup code here if needed


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for testing URL fetching"""
    with patch("requests.get") as mock:
        response = Mock()
        response.content = b"Mock file content"
        response.raise_for_status = Mock()
        mock.return_value = response
        yield mock
