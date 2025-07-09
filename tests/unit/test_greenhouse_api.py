"""
Unit tests for GreenhouseClient class
"""

import base64
import json
import urllib.error
from unittest.mock import Mock, patch

import pytest

from hirescope.greenhouse_api import GreenhouseClient


class TestGreenhouseClient:
    """Test suite for GreenhouseClient class"""

    @pytest.fixture
    def client(self):
        """Create a GreenhouseClient instance for testing"""
        return GreenhouseClient("test_api_key_123")

    @pytest.fixture
    def mock_urlopen(self):
        """Mock urllib.request.urlopen"""
        with patch("urllib.request.urlopen") as mock:
            yield mock

    def test_init_proper_credentials(self):
        """Test proper initialization and credential encoding"""
        client = GreenhouseClient("my_secret_key")

        # Check API key is stored
        assert client.api_key == "my_secret_key"

        # Check base64 encoding is correct
        expected_creds = base64.b64encode(b"my_secret_key:").decode()
        assert client.credentials == expected_creds

        # Check base URL
        assert client.base_url == "https://harvest.greenhouse.io/v1"

    # Tests for _make_request method
    def test_make_request_success(self, client, mock_urlopen):
        """Test successful API request"""
        # Mock response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(
            {"id": 123, "name": "Test"}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Make request
        result = client._make_request("jobs/123")

        # Verify
        assert result == {"id": 123, "name": "Test"}
        mock_urlopen.assert_called_once()

        # Check request was built correctly
        request = mock_urlopen.call_args[0][0]
        assert request.full_url == "https://harvest.greenhouse.io/v1/jobs/123"
        assert request.headers["Authorization"] == f"Basic {client.credentials}"

    @patch("time.sleep")
    def test_make_request_rate_limited(self, mock_sleep, client, mock_urlopen):
        """Test rate limiting handling with retry"""
        # First call: rate limited
        error_429 = urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None)

        # Second call: success
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({"success": True}).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)

        mock_urlopen.side_effect = [error_429, mock_response]

        # Make request
        result = client._make_request("jobs")

        # Verify retry happened
        assert result == {"success": True}
        assert mock_urlopen.call_count == 2
        mock_sleep.assert_called_once_with(60)

    def test_make_request_forbidden(self, client, mock_urlopen):
        """Test 403 forbidden error handling"""
        error_403 = urllib.error.HTTPError("url", 403, "Forbidden", {}, None)
        mock_urlopen.side_effect = error_403

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            client._make_request("jobs/123")

        assert "Permission denied" in str(exc_info.value)
        assert "jobs/123" in str(exc_info.value)

    def test_make_request_other_http_error(self, client, mock_urlopen):
        """Test other HTTP errors"""
        error_500 = urllib.error.HTTPError(
            "url", 500, "Internal Server Error", {}, None
        )
        mock_urlopen.side_effect = error_500

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            client._make_request("jobs")

        assert "API error 500" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)

    # Tests for get_job method
    def test_get_job_success(self, client, mock_urlopen):
        """Test successful job retrieval"""
        job_data = {
            "id": 123,
            "name": "Software Engineer",
            "departments": [{"name": "Engineering"}],
            "offices": [{"name": "Remote"}],
        }

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(job_data).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = client.get_job(123)

        assert result == job_data
        assert "jobs/123" in mock_urlopen.call_args[0][0].full_url

    # Tests for get_jobs_with_applications method
    @patch("builtins.print")
    def test_get_jobs_with_applications_single_page(self, mock_print, client):
        """Test getting jobs with applications - single page"""
        # Mock responses
        jobs_response = [
            {
                "id": 1,
                "name": "Job 1",
                "status": "open",
                "departments": [{"name": "Eng"}],
                "created_at": "2024-01-01",
            },
            {
                "id": 2,
                "name": "Job 2",
                "status": "closed",
                "departments": [],
                "created_at": "2024-01-02",
            },
        ]

        # Patch _make_request instead of urlopen for simpler mocking
        with patch.object(client, "_make_request") as mock_request:
            # Set up the sequence of responses
            mock_request.side_effect = [
                jobs_response,  # Jobs page 1
                [{"id": 100, "candidate_id": 1}],  # Apps for job 1
                [],  # Apps for job 2 (no applications)
                [],  # Jobs page 2 (empty)
            ]

            result = client.get_jobs_with_applications()

            # Should only return job 1 (has applications)
            assert len(result) == 1
            assert result[0]["id"] == 1
            assert result[0]["name"] == "Job 1"
            assert result[0]["department"] == "Eng"
            assert result[0]["application_count"] == 1

    def test_get_jobs_with_applications_pagination(self, client):
        """Test jobs pagination"""
        # Create 150 jobs across 2 pages
        jobs_page1 = [
            {
                "id": i,
                "name": f"Job {i}",
                "status": "open",
                "departments": [{"name": "Dept"}],
                "created_at": "2024-01-01",
            }
            for i in range(1, 101)
        ]
        jobs_page2 = [
            {
                "id": i,
                "name": f"Job {i}",
                "status": "open",
                "departments": [{"name": "Dept"}],
                "created_at": "2024-01-01",
            }
            for i in range(101, 151)
        ]

        with patch.object(client, "_make_request") as mock_request:
            responses = []
            # First page of jobs
            responses.append(jobs_page1)

            # Add application check responses for page 1 jobs (all have apps)
            for _ in range(100):
                responses.append([{"id": 1}])

            # Second page of jobs
            responses.append(jobs_page2)

            # Add application check responses for page 2 jobs (all have apps)
            for _ in range(50):
                responses.append([{"id": 1}])

            # Empty page to end pagination
            responses.append([])

            mock_request.side_effect = responses

            result = client.get_jobs_with_applications()

            assert len(result) == 150

    def test_get_jobs_with_applications_error_handling(self, client, mock_urlopen):
        """Test error handling during job fetching"""
        jobs_response = [
            {
                "id": 1,
                "name": "Job 1",
                "status": "open",
                "departments": [{"name": "Eng"}],
                "created_at": "2024-01-01",
            }
        ]

        responses = [
            Mock(read=lambda: json.dumps(jobs_response).encode()),  # Jobs page 1
            Mock(read=lambda: json.dumps([]).encode()),  # Jobs page 2 (empty)
        ]

        # Application check fails
        error = urllib.error.HTTPError("url", 500, "Server Error", {}, None)
        responses.append(error)

        for resp in responses[:-1]:
            resp.__enter__ = lambda self: self
            resp.__exit__ = lambda self, *args: None

        mock_urlopen.side_effect = responses

        result = client.get_jobs_with_applications()

        # Should return empty list as job check failed
        assert result == []

    # Tests for get_applications method
    def test_get_applications_single_page(self, client, mock_urlopen):
        """Test getting applications - single page"""
        apps_data = [{"id": 1, "candidate_id": 100}, {"id": 2, "candidate_id": 101}]

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(apps_data).encode()
        mock_response.__enter__ = lambda self: self
        mock_response.__exit__ = lambda self, *args: None

        # First call returns data, second returns empty
        mock_urlopen.side_effect = [
            mock_response,
            Mock(
                __enter__=lambda self: Mock(read=lambda: b"[]"),
                __exit__=lambda self, *args: None,
            ),
        ]

        result = client.get_applications(123)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_get_applications_with_limit(self, client, mock_urlopen):
        """Test getting applications with limit"""
        # Create 150 applications
        apps_page1 = [{"id": i, "candidate_id": i} for i in range(100)]
        apps_page2 = [{"id": i, "candidate_id": i} for i in range(100, 150)]

        responses = [
            Mock(read=lambda: json.dumps(apps_page1).encode()),
            Mock(read=lambda: json.dumps(apps_page2).encode()),
        ]

        for resp in responses:
            resp.__enter__ = lambda self: self
            resp.__exit__ = lambda self, *args: None

        mock_urlopen.side_effect = responses

        result = client.get_applications(123, limit=75)

        assert len(result) == 75

    @patch("builtins.print")
    def test_get_applications_error_handling(self, mock_print, client, mock_urlopen):
        """Test error handling during application fetching"""
        # First page succeeds
        apps_page1 = [{"id": 1, "candidate_id": 100}]
        mock_response1 = Mock(read=lambda: json.dumps(apps_page1).encode())
        mock_response1.__enter__ = lambda self: self
        mock_response1.__exit__ = lambda self, *args: None

        # Second page fails
        error = Exception("Network error")

        mock_urlopen.side_effect = [mock_response1, error]

        result = client.get_applications(123)

        # Should return partial results
        assert len(result) == 1
        assert "Error fetching applications page 2" in mock_print.call_args[0][0]

    # Tests for get_candidate method
    def test_get_candidate_success(self, client, mock_urlopen):
        """Test successful candidate retrieval"""
        candidate_data = {
            "id": 100,
            "first_name": "John",
            "last_name": "Doe",
            "email_addresses": [{"value": "john@example.com"}],
        }

        mock_response = Mock()
        mock_response.read.return_value = json.dumps(candidate_data).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = client.get_candidate(100)

        assert result == candidate_data

    @patch("builtins.print")
    def test_get_candidate_not_found(self, mock_print, client, mock_urlopen):
        """Test candidate not found"""
        error = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
        mock_urlopen.side_effect = error

        result = client.get_candidate(999)

        assert result is None
        assert "Could not fetch candidate 999" in mock_print.call_args[0][0]

    # Tests for download_attachment method
    def test_download_attachment_success(self, client, mock_urlopen):
        """Test successful attachment download"""
        pdf_content = b"%PDF-1.4 fake pdf content"

        mock_response = Mock()
        mock_response.read.return_value = pdf_content
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = client.download_attachment("https://example.com/file.pdf")

        assert result == pdf_content

    @patch("builtins.print")
    def test_download_attachment_failure(self, mock_print, client, mock_urlopen):
        """Test attachment download failure"""
        error = urllib.error.URLError("Connection failed")
        mock_urlopen.side_effect = error

        result = client.download_attachment("https://example.com/file.pdf")

        assert result is None
        assert "Download failed" in mock_print.call_args[0][0]

    def test_download_attachment_empty_file(self, client, mock_urlopen):
        """Test downloading empty attachment"""
        mock_response = Mock()
        mock_response.read.return_value = b""
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = client.download_attachment("https://example.com/empty.pdf")

        assert result == b""

    # Edge case tests
    def test_get_jobs_missing_department_data(self, client):
        """Test handling missing department data"""
        # Job 1: No departments key - uses default [{}] which works
        # Job 2: Empty departments list - will cause IndexError and be skipped
        # Job 3: Normal case with department
        jobs_response = [
            {"id": 1, "name": "Job 1", "status": "open", "created_at": "2024-01-01"},
            {
                "id": 2,
                "name": "Job 2",
                "status": "open",
                "departments": [],
                "created_at": "2024-01-02",
            },
            {
                "id": 3,
                "name": "Job 3",
                "status": "open",
                "departments": [{"name": "HR"}],
                "created_at": "2024-01-03",
            },
        ]

        with patch.object(client, "_make_request") as mock_request:
            # All 3 jobs will have their applications checked
            mock_request.side_effect = [
                jobs_response,  # Jobs page 1
                [{"id": 1}],  # Apps check for job 1 (has apps)
                [{"id": 2}],  # Apps check for job 2 (has apps)
                [{"id": 3}],  # Apps check for job 3 (has apps)
                [],  # Jobs page 2 (empty)
            ]

            result = client.get_jobs_with_applications()

            # Job 2 will be skipped due to IndexError when accessing empty departments list
            assert len(result) == 2
            # Check they're sorted by created_at (newest first)
            assert result[0]["id"] == 3  # 2024-01-03 is newest
            assert result[1]["id"] == 1  # 2024-01-01 is oldest
            assert result[0]["department"] == "HR"
            assert result[1]["department"] == "N/A"  # No departments key
