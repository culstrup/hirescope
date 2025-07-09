"""
Unit tests for AIScorer class
"""

import json
import urllib.error
from unittest.mock import Mock, patch

import pytest

from hirescope.ai_scorer import AIScorer


class TestAIScorer:
    """Test suite for AIScorer class"""

    @pytest.fixture
    def scorer(self):
        """Create an AIScorer instance for testing"""
        return AIScorer("test_api_key")

    @pytest.fixture
    def sample_candidate_profile(self):
        """Sample candidate profile text for testing"""
        return """
Name: Jane Smith
Email: jane@example.com
Phone: 555-1234

RESUME:
Senior Software Engineer with 8 years experience in Python, AWS, and distributed systems.
Led team of 5 engineers. Improved system performance by 50%.

COVER LETTER:
I am excited to apply for this position at your company...

LINKEDIN: https://linkedin.com/in/janesmith
GITHUB: https://github.com/janesmith

APPLICATION QUESTIONS:
Q: Years of experience?
A: 8 years

Q: Salary expectations?
A: $150,000
"""

    @pytest.fixture
    def sample_job_description(self):
        """Sample job description for testing"""
        return """
We are looking for a Senior Software Engineer to join our Engineering team.

Requirements:
- 8+ years of software engineering experience
- Strong Python and AWS skills
- Experience with distributed systems
- Leadership experience

Responsibilities:
- Design and implement scalable systems
- Lead technical initiatives
- Mentor junior engineers
"""

    @pytest.fixture
    def sample_company_context(self):
        """Sample company context for testing"""
        return "Fast-paced startup environment focused on innovation and collaboration"

    def test_init(self):
        """Test AIScorer initialization"""
        scorer = AIScorer("my_api_key")
        assert scorer.api_key == "my_api_key"
        assert scorer.api_url == "https://api.openai.com/v1/chat/completions"
        assert scorer.model == "o3"
        assert scorer.max_retries == 3

    @patch("urllib.request.urlopen")
    def test_score_candidate_success(
        self, mock_urlopen, scorer, sample_candidate_profile, sample_job_description
    ):
        """Test successful candidate scoring"""
        # Mock the API response
        api_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "score": 85,
                                "summary": "Strong candidate with relevant experience",
                                "key_strengths": [
                                    "Python expertise",
                                    "AWS experience",
                                    "Leadership",
                                ],
                                "concerns": ["Limited experience with our tech stack"],
                                "hire_recommendation": "Strong Yes - excellent technical match",
                                "notable_achievements": [
                                    "Led team of 5",
                                    "Improved performance by 50%",
                                ],
                                "culture_fit": "Excellent fit for startup environment",
                                "data_quality": "Complete profile with all relevant information",
                            }
                        )
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 1000,
                "completion_tokens": 200,
                "reasoning_tokens": 300,
            },
        }

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(api_response).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response

        # Score the candidate
        result = scorer.score_candidate(
            job_title="Senior Software Engineer",
            job_description=sample_job_description,
            candidate_profile=sample_candidate_profile,
        )

        # Verify the result
        assert result["score"] == 85
        assert result["summary"] == "Strong candidate with relevant experience"
        assert len(result["key_strengths"]) == 3
        assert "Strong Yes" in result["hire_recommendation"]
        assert result["culture_fit"] == "Excellent fit for startup environment"
        assert (
            result["data_quality"] == "Complete profile with all relevant information"
        )
        assert "cost" in result

        # Verify API request
        mock_urlopen.assert_called_once()
        request = mock_urlopen.call_args[0][0]
        assert request.full_url == "https://api.openai.com/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test_api_key"

    @patch("urllib.request.urlopen")
    def test_score_candidate_with_company_context(
        self,
        mock_urlopen,
        scorer,
        sample_candidate_profile,
        sample_job_description,
        sample_company_context,
    ):
        """Test scoring with company context"""
        # Mock the API response
        api_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "score": 75,
                                "summary": "Good candidate",
                                "key_strengths": ["Technical skills"],
                                "concerns": ["Culture fit"],
                                "hire_recommendation": "Yes",
                                "notable_achievements": ["Award winner"],
                                "culture_fit": "Good",
                                "data_quality": "Medium",
                            }
                        )
                    }
                }
            ],
            "usage": {"prompt_tokens": 1200, "completion_tokens": 150},
        }

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(api_response).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response

        # Score with company context
        result = scorer.score_candidate(
            job_title="Senior Software Engineer",
            job_description=sample_job_description,
            candidate_profile=sample_candidate_profile,
            company_context=sample_company_context,
        )

        # Verify company context was included in request
        request = mock_urlopen.call_args[0][0]
        request_data = json.loads(request.data.decode())
        user_message = request_data["messages"][1]["content"]
        assert "COMPANY CONTEXT:" in user_message
        assert sample_company_context in user_message

    @patch("urllib.request.urlopen")
    def test_score_candidate_json_parse_error(
        self, mock_urlopen, scorer, sample_candidate_profile, sample_job_description
    ):
        """Test handling of invalid JSON response"""
        # Mock response with invalid JSON
        api_response = {
            "choices": [{"message": {"content": "Invalid JSON response"}}],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 100},
        }

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(api_response).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response

        # Score should return error response
        result = scorer.score_candidate(
            job_title="Senior Software Engineer",
            job_description=sample_job_description,
            candidate_profile=sample_candidate_profile,
        )

        assert result["score"] == 0
        assert "Scoring failed" in result["summary"]
        assert result["concerns"] == ["Unable to complete AI evaluation"]
        assert result["hire_recommendation"] == "Unable to assess"
        assert result["error"] is True

    @patch("urllib.request.urlopen")
    @patch("time.sleep")
    def test_score_candidate_rate_limit_retry(
        self,
        mock_sleep,
        mock_urlopen,
        scorer,
        sample_candidate_profile,
        sample_job_description,
    ):
        """Test rate limit handling with retry"""
        # First call: rate limited
        error_429 = urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None)

        # Second call: success
        api_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "score": 70,
                                "summary": "Decent candidate",
                                "key_strengths": ["Experience"],
                                "concerns": ["Skills gap"],
                                "hire_recommendation": "Maybe",
                                "notable_achievements": ["Project lead"],
                                "culture_fit": "Good",
                                "data_quality": "Medium",
                            }
                        )
                    }
                }
            ],
            "usage": {"prompt_tokens": 900, "completion_tokens": 180},
        }

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(api_response).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)

        mock_urlopen.side_effect = [error_429, mock_response]

        # Should retry and succeed
        result = scorer.score_candidate(
            job_title="Senior Software Engineer",
            job_description=sample_job_description,
            candidate_profile=sample_candidate_profile,
        )

        assert result["score"] == 70
        assert mock_urlopen.call_count == 2
        mock_sleep.assert_called_once_with(30)  # First retry waits 30s

    @patch("urllib.request.urlopen")
    @patch("time.sleep")
    def test_score_candidate_all_retries_fail(
        self,
        mock_sleep,
        mock_urlopen,
        scorer,
        sample_candidate_profile,
        sample_job_description,
    ):
        """Test failure after all retries"""
        # All calls fail
        error = Exception("Persistent API Error")
        mock_urlopen.side_effect = error

        # Should return error response after retries
        result = scorer.score_candidate(
            job_title="Senior Software Engineer",
            job_description=sample_job_description,
            candidate_profile=sample_candidate_profile,
        )

        assert result["score"] == 0
        assert "Scoring failed" in result["summary"]
        assert result["hire_recommendation"] == "Unable to assess"
        assert result["error"] is True
        assert mock_urlopen.call_count == 3  # All retries attempted

    @patch("urllib.request.urlopen")
    def test_score_candidate_http_error(
        self, mock_urlopen, scorer, sample_candidate_profile, sample_job_description
    ):
        """Test handling of non-429 HTTP errors"""
        # Mock 500 error - let the actual code handle the error
        error_500 = urllib.error.HTTPError(
            "url", 500, "Internal Server Error", {}, None
        )

        mock_urlopen.side_effect = error_500

        result = scorer.score_candidate(
            job_title="Senior Software Engineer",
            job_description=sample_job_description,
            candidate_profile=sample_candidate_profile,
        )

        assert result["score"] == 0
        assert result["error"] is True
        assert result["hire_recommendation"] == "Unable to assess"

    def test_calculate_cost(self, scorer):
        """Test cost calculation"""
        # Test with all token types
        usage = {
            "prompt_tokens": 2000,
            "completion_tokens": 500,
            "reasoning_tokens": 300,
        }

        cost = scorer._calculate_cost(usage)

        # Expected: (2000/1000 * 0.015) + (500/1000 * 0.060) + (300/1000 * 0.060)
        # = 0.03 + 0.03 + 0.018 = 0.078
        assert cost == pytest.approx(0.078, rel=1e-3)

    def test_calculate_cost_empty_usage(self, scorer):
        """Test cost calculation with empty usage"""
        cost = scorer._calculate_cost({})
        assert cost == 0.0

    def test_calculate_cost_partial_usage(self, scorer):
        """Test cost calculation with partial usage data"""
        usage = {
            "prompt_tokens": 1000,
            # Missing other token types
        }

        cost = scorer._calculate_cost(usage)

        # Only prompt tokens: 1000/1000 * 0.015 = 0.015
        assert cost == 0.015

    @patch("urllib.request.urlopen")
    def test_prompt_construction(
        self, mock_urlopen, scorer, sample_candidate_profile, sample_job_description
    ):
        """Test that prompt is constructed correctly"""
        # Mock successful response
        api_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "score": 80,
                                "summary": "Good match",
                                "key_strengths": ["Skills"],
                                "concerns": [],
                                "hire_recommendation": "Yes",
                                "notable_achievements": [],
                                "culture_fit": "Good",
                                "data_quality": "High",
                            }
                        )
                    }
                }
            ],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 100},
        }

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(api_response).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_urlopen.return_value = mock_response

        # Score candidate
        scorer.score_candidate(
            job_title="Senior Software Engineer",
            job_description=sample_job_description,
            candidate_profile=sample_candidate_profile,
        )

        # Verify request structure
        request = mock_urlopen.call_args[0][0]
        request_data = json.loads(request.data.decode())

        assert request_data["model"] == "o3"
        assert request_data["max_completion_tokens"] == 2000
        assert request_data["reasoning_effort"] == "medium"
        assert request_data["response_format"]["type"] == "json_object"

        # Check messages
        assert len(request_data["messages"]) == 2
        assert request_data["messages"][0]["role"] == "developer"
        assert "expert recruiter" in request_data["messages"][0]["content"]
        assert request_data["messages"][1]["role"] == "user"

        # Check prompt content
        user_message = request_data["messages"][1]["content"]
        assert "Senior Software Engineer" in user_message
        assert sample_job_description in user_message
        assert sample_candidate_profile in user_message
        assert "Skills and experience match (40 points max)" in user_message
