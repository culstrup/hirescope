# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the HireScope codebase.

## HireScope Overview

HireScope is an AI-powered candidate analysis tool that integrates with Greenhouse ATS to evaluate job applicants using OpenAI's o3 model. The key value proposition is finding "hidden gems" - previously rejected candidates who score highly in AI evaluation (20-40% of top candidates in real-world testing).

## Project Context

- **Author**: GSD at Work LLC (https://gsdat.work)
- **Repository**: https://github.com/culstrup/hirescope
- **License**: MIT
- **Purpose**: Open source tool for any company using Greenhouse ATS
- **Key Stat**: 20-40% of top recommended candidates are typically "hidden gems" (previously rejected)

## Key Commands

### Setup and Installation
```bash
# Quick setup (recommended)
./setup.sh

# Manual setup if needed
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
```

### Running HireScope
```bash
# Activate environment and run
source venv/bin/activate
python hirescope.py
```

### Git Operations
```bash
# Common git commands for this project
git status
git add .
git commit -m "message"
git push origin main
```

## Architecture Overview

### Core Components

1. **hirescope.py** - Main CLI entry point
   - Interactive menu for job selection
   - Orchestrates the analysis workflow
   - Path manipulation: `sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hirescope'))`

2. **hirescope/analyzer.py** - Central orchestration (`CandidateAnalyzer` class)
   - Manages job description extraction (often missing from Greenhouse API)
   - Implements progress saving every 10 candidates
   - Builds comprehensive candidate profiles from multiple data sources

3. **hirescope/greenhouse_api.py** - API Integration (`GreenhouseClient` class)
   - Handles Greenhouse Harvest API v1 authentication
   - Implements pagination for large candidate lists
   - Rate limiting and 403/429 error handling
   - Key limitation: Job descriptions often not available in API

4. **hirescope/document_processor.py** - Resume/Attachment Processing (`DocumentProcessor` class)
   - Extracts text from PDF (PyPDF2) and DOCX (python-docx)
   - Detects image-based PDFs (cannot extract)
   - Currently missing: TXT, DOC format support

5. **hirescope/ai_scorer.py** - OpenAI Integration (`AIScorer` class)
   - Uses o3 model with `reasoning_effort="medium"`
   - Scoring criteria: Skills (40pts), Achievements (30pts), Culture Fit (20pts), Growth (10pts)
   - Implements retry logic for rate limits
   - Cost tracking (~$0.02 per candidate)

6. **hirescope/report_generator.py** - Output Generation (`ReportGenerator` class)
   - Creates three outputs: Markdown report, CSV summary, JSON data
   - Generates Greenhouse profile links: `https://app8.greenhouse.io/people/{candidate_id}/applications/{application_id}`
   - Identifies "hidden gems" (rejected candidates with score >= 70)

### Key Design Patterns

1. **Import Structure**: Uses absolute imports within hirescope package (no dots)
2. **Progress Persistence**: Saves `progress_*.json` files every 10 candidates
3. **Job Description Workaround**: Builds descriptions from metadata and application questions when API returns empty
4. **Error Handling**: Connection resets and rate limits are expected and handled gracefully

## Critical Implementation Details

### Greenhouse API Limitations
- Job descriptions (`notes` field) usually empty in API response
- Must build context from custom fields, departments, and application questions
- Permissions required: Applications (GET), Candidates (GET), Jobs (GET)

### Document Processing
- ~98.7% success rate for PDF/DOCX extraction
- Image-based PDFs detected but not processed (potential OCR enhancement)
- Missing attachments logged but don't stop analysis

### Cost Management
- OpenAI API costs tracked per candidate (~$0.02 each)
- Checkpointing allows resuming expensive analyses
- Total cost displayed in final report

### AI Scoring Details
- Model: OpenAI o3 with `reasoning_effort="medium"`
- Evaluation returns JSON with:
  - score (0-100)
  - summary
  - key_strengths
  - concerns
  - hire_recommendation
  - notable_achievements
  - culture_fit
  - data_quality

## Output Files

Generated in current directory:
- `REPORT_{JobName}_{Timestamp}.md` - Main analysis report with all candidates
- `TOP_CANDIDATES_{JobName}_{Timestamp}.csv` - Quick reference for top candidates
- `RESULTS_{JobName}_{Timestamp}.json` - Complete data for further processing

## Known Issues and Limitations

1. **Import error if running from different directory** - Fixed by path manipulation in hirescope.py
2. **No automated tests** - Reliability depends on manual testing
3. **Job descriptions often missing from Greenhouse API** - Workaround implemented
4. **Cannot process image-based PDFs or legacy DOC files** - Detected and logged
5. **Rate limiting can slow analysis of large candidate pools** - Retry logic implemented

## Development Guidelines

### When Making Changes
1. **Maintain import structure** - Use absolute imports, not relative
2. **Follow error handling patterns** - Graceful degradation for missing data
3. **Update cost calculations** - If OpenAI pricing changes
4. **Test with real Greenhouse data** - No mock testing framework exists

### Adding New Features
1. **OCR support** - For image-based PDFs (high value addition)
2. **Additional file formats** - TXT, DOC support
3. **Batch processing** - Analyze multiple jobs in sequence
4. **Resume parsing improvements** - Better structure extraction

### Code Style
- Python 3.8+ required
- Follow existing patterns in the codebase
- Use type hints where beneficial
- Keep functions focused and testable

## Environment Variables

Required in `.env`:
```
GREENHOUSE_API_KEY=your_harvest_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

Optional:
```
COMPANY_CONTEXT="Your company culture and values for better AI alignment"
```

## Common Tasks

### Analyzing a New Job
1. Ensure API keys are set in `.env`
2. Run `python hirescope.py`
3. Select job from menu
4. Specify number of top candidates (5-20)
5. Optionally add company context
6. Wait for analysis to complete
7. Review output files

### Resuming Interrupted Analysis
- Progress saves automatically every 10 candidates
- Simply re-run the same job analysis
- System will detect and continue from last checkpoint

### Debugging API Issues
1. Check Greenhouse permissions (need read access to jobs, candidates, applications)
2. Verify API key is Harvest API v1 (not Job Board API)
3. Check rate limits (429 errors are handled automatically)
4. Review console output for specific error messages

## Historical Context

This project was originally created as "HireScope Candidate Analyzer" for internal use at HireScope, analyzing their historical candidate data. It was then generalized and open-sourced as HireScope, removing all company-specific references. The core value discovered during initial testing was that 20-40% of the highest-scoring candidates were found in the previously rejected pool, highlighting potential bias or oversights in manual screening processes.