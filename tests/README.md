# HireScope Tests

This directory contains all tests for the HireScope project.

## Structure

```
tests/
├── conftest.py          # Shared pytest fixtures
├── fixtures/            # Test data and mock responses
│   ├── api_responses/   # Mock API responses
│   └── sample_resumes/  # Sample documents for testing
├── unit/               # Unit tests for individual components
│   └── test_document_processor.py
└── integration/        # Integration tests (coming soon)
```

## Running Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=hirescope

# Run specific test file
pytest tests/unit/test_document_processor.py -v
```

### Using Make
```bash
# Run unit tests
make test

# Run all tests with coverage
make test-all

# Run linting and formatting
make lint
make format

# Run all pre-commit checks
make pre-commit
```

## Writing Tests

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<what_is_being_tested>`

### Example Test Structure
```python
class TestDocumentProcessor:
    """Test suite for DocumentProcessor class"""
    
    @pytest.fixture
    def processor(self):
        """Create a processor instance for testing"""
        return DocumentProcessor()
    
    def test_extract_pdf_success(self, processor):
        """Test successful PDF extraction"""
        # Given
        content = b"fake pdf content"
        
        # When
        result = processor.extract_text(content, "test.pdf")
        
        # Then
        assert "expected text" in result
```

### Using Fixtures

Common fixtures are defined in `conftest.py`:
- `load_fixture()` - Load JSON test data
- `mock_greenhouse_client` - Mocked Greenhouse API client
- `mock_openai_client` - Mocked OpenAI client
- `sample_resume_text` - Sample resume content
- `sample_cover_letter_text` - Sample cover letter content

## Coverage Goals

- Target: 80% overall coverage
- Critical paths: 90%+ coverage
- New code: Must include tests

## CI/CD Integration

Tests run automatically on:
- Every push to `main`
- Every pull request
- Multiple Python versions (3.8-3.11)

See `.github/workflows/ci.yml` for details.