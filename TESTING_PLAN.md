# HireScope Testing & CI/CD Plan

## Overview
This document outlines a comprehensive testing strategy and CI/CD implementation plan for HireScope to ensure code quality, reliability, and professional development practices.

## 1. Testing Strategy

### 1.1 Test Pyramid Approach
```
         /\
        /  \    E2E Tests (10%)
       /    \   - Full workflow tests
      /------\  
     /        \ Integration Tests (30%)
    /          \- API integrations
   /            \- Component interactions
  /--------------\
 /                \ Unit Tests (60%)
/                  \- Core logic
--------------------\- Utilities
```

### 1.2 Key Testing Areas

#### Unit Tests
- **Document Processing** (`test_document_processor.py`)
  - PDF text extraction
  - DOCX text extraction
  - Image-based PDF detection
  - Error handling for corrupt files
  
- **AI Scoring** (`test_ai_scorer.py`)
  - Score calculation logic
  - JSON response parsing
  - Retry mechanism
  - Cost calculation
  
- **Report Generation** (`test_report_generator.py`)
  - Markdown formatting
  - CSV generation
  - File path handling
  - Score sorting

#### Integration Tests
- **Greenhouse API** (`test_greenhouse_integration.py`)
  - Authentication
  - Rate limiting handling
  - Pagination
  - Data transformation
  
- **OpenAI Integration** (`test_openai_integration.py`)
  - API connectivity
  - Response validation
  - Error handling
  - Mock responses for CI

#### End-to-End Tests
- **Full Analysis Workflow** (`test_e2e_workflow.py`)
  - Job selection
  - Candidate analysis
  - Report generation
  - Progress resumption

### 1.3 Test Data Strategy
```
tests/
├── fixtures/
│   ├── sample_resumes/
│   │   ├── valid_pdf.pdf
│   │   ├── image_based.pdf
│   │   └── valid_docx.docx
│   ├── api_responses/
│   │   ├── greenhouse_jobs.json
│   │   ├── greenhouse_candidates.json
│   │   └── openai_scoring.json
│   └── expected_outputs/
│       ├── report_template.md
│       └── csv_template.csv
```

## 2. Testing Tools & Configuration

### 2.1 Core Testing Stack
```toml
# pyproject.toml
[tool.pytest]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=hirescope --cov-report=term-missing --cov-report=html"

[tool.coverage]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### 2.2 Testing Dependencies
```txt
# requirements-dev.txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-asyncio>=0.21.0
responses>=0.23.0  # For mocking HTTP requests
freezegun>=1.2.0   # For time-based testing
factory-boy>=3.3.0 # For test data generation
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
pre-commit>=3.4.0
```

## 3. CI/CD Pipeline (GitHub Actions)

### 3.1 Main Workflow
```yaml
# .github/workflows/main.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with ruff
      run: ruff check .
    
    - name: Format check with black
      run: black --check .
    
    - name: Type check with mypy
      run: mypy hirescope/
    
    - name: Run tests
      env:
        GREENHOUSE_API_KEY: ${{ secrets.TEST_GREENHOUSE_KEY }}
        OPENAI_API_KEY: ${{ secrets.TEST_OPENAI_KEY }}
      run: |
        pytest --cov=hirescope --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 3.2 Security Scanning
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Bandit Security Scan
      uses: gaurav-nelson/bandit-action@v1
      with:
        path: "hirescope/"
    
    - name: Check dependencies with Safety
      run: |
        pip install safety
        safety check --json
```

## 4. Development Workflow

### 4.1 Branch Protection Rules
- Require PR reviews before merging
- Require status checks to pass (tests, linting, type checking)
- Require branches to be up to date before merging
- Enforce linear history (optional)

### 4.2 PR Template
```markdown
<!-- .github/pull_request_template.md -->
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No sensitive data exposed
```

### 4.3 Commit Convention
```
feat: Add batch processing for multiple jobs
fix: Handle rate limiting in Greenhouse API
docs: Update installation instructions
test: Add unit tests for document processor
refactor: Simplify candidate scoring logic
chore: Update dependencies
```

## 5. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up pytest and basic test structure
- [ ] Create test fixtures and mock data
- [ ] Write unit tests for document_processor.py
- [ ] Set up pre-commit hooks
- [ ] Create basic GitHub Actions workflow

### Phase 2: Core Testing (Week 3-4)
- [ ] Unit tests for ai_scorer.py
- [ ] Unit tests for report generators
- [ ] Integration tests with mocked APIs
- [ ] Add coverage reporting
- [ ] Implement branch protection rules

### Phase 3: Advanced Testing (Week 5-6)
- [ ] E2E workflow tests
- [ ] Performance benchmarks
- [ ] Security scanning integration
- [ ] Documentation for test writing
- [ ] Test data management system

### Phase 4: Optimization (Ongoing)
- [ ] Parallel test execution
- [ ] Test result caching
- [ ] Flaky test detection
- [ ] Performance monitoring
- [ ] Automated dependency updates

## 6. Mock Strategy for External APIs

### 6.1 Greenhouse API Mocks
```python
# tests/mocks/greenhouse_mock.py
class MockGreenhouseClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.jobs_data = load_fixture('greenhouse_jobs.json')
        self.candidates_data = load_fixture('greenhouse_candidates.json')
    
    def get_jobs(self):
        return self.jobs_data
    
    def get_candidates(self, job_id: int):
        return self.candidates_data.get(str(job_id), [])
```

### 6.2 OpenAI API Mocks
```python
# tests/mocks/openai_mock.py
class MockAIScorer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.responses = load_fixture('openai_responses.json')
    
    def score_candidate(self, profile: str, job_desc: str):
        # Return deterministic scores based on candidate name
        return self.responses.get(hash(profile) % len(self.responses))
```

## 7. Monitoring & Metrics

### 7.1 Key Metrics to Track
- Test coverage (target: >80%)
- Test execution time
- Flaky test rate
- PR merge time
- Build success rate

### 7.2 Dashboard Integration
- Codecov for coverage visualization
- GitHub Actions insights
- Custom metrics in README badges

## 8. Documentation Standards

### 8.1 Test Documentation
```python
def test_extract_pdf_with_images():
    """
    Test PDF extraction with embedded images.
    
    Given: A PDF file with text and images
    When: extract_text() is called
    Then: Only text content should be returned
    """
```

### 8.2 Test Naming Convention
- `test_<method>_<scenario>_<expected_result>`
- Example: `test_score_candidate_with_missing_resume_returns_low_score`

## 9. Emergency Procedures

### 9.1 Handling Test Failures in Production
1. Revert to last known good commit
2. Run emergency test suite
3. Deploy hotfix with bypass (requires 2 approvals)
4. Retrospective within 24 hours

### 9.2 API Key Rotation
- Automated monthly rotation for test keys
- Secure storage in GitHub Secrets
- Notification system for expiring keys

## 10. Success Criteria

### Short Term (3 months)
- [ ] 80% code coverage
- [ ] All PRs require passing tests
- [ ] <5 minute CI pipeline
- [ ] Zero security vulnerabilities

### Long Term (6 months)
- [ ] 90% code coverage
- [ ] Automated performance regression detection
- [ ] Full E2E test suite
- [ ] Automated release process

---

**Note**: This plan is designed to be implemented incrementally. Start with Phase 1 and gradually build up the testing infrastructure while maintaining development velocity.