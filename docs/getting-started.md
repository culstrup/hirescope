# Getting Started with HireScope

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed on your system
2. **Greenhouse account** with API access
3. **OpenAI account** with API access to o3 model
4. **Git** (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/culstrup/hirescope.git
cd hirescope
```

### 2. Run the Setup Script

```bash
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create a `.env` file from the template

### 3. Configure API Keys

Edit the `.env` file with your API keys:

```bash
nano .env
```

Add your keys:
```
GREENHOUSE_API_KEY=your_greenhouse_key_here
OPENAI_API_KEY=sk-your_openai_key_here
```

#### Getting Your Greenhouse API Key

1. Log into Greenhouse as an Admin
2. Navigate to: Configure > Dev Center > API Credential Management
3. Click "Create New API Key"
4. Select type: "Harvest"
5. Grant permissions:
   - Applications: GET
   - Candidates: GET  
   - Jobs: GET

#### Getting Your OpenAI API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key (you won't be able to see it again!)
4. Ensure you have access to the o3 model

## Running Your First Analysis

### 1. Activate the Virtual Environment

```bash
source venv/bin/activate
```

### 2. Run HireScope

```bash
python hirescope.py
```

### 3. Select a Job

You'll see a list of all jobs with applications:

```
🎯 AVAILABLE JOBS FOR ANALYSIS (5 total)
================================================================================
#    Status   Job Title                                Department            Created
--------------------------------------------------------------------------------
1    🟢 OPEN   Senior Software Engineer                 Engineering          2025-01-15
2    🟢 OPEN   Product Manager                         Product              2025-01-08
3    🔴 CLOSED Staff Accountant                        Finance              2024-12-20
```

Enter the number of the job you want to analyze.

### 4. Configure Analysis

- **Number of top candidates**: How many top candidates to identify (5-20)
- **Company context**: Optional description of your company culture

### 5. Review Results

After analysis completes, you'll get:

- **Markdown report**: Comprehensive analysis with all details
- **CSV file**: Top candidates for easy sharing
- **JSON file**: Complete data for further analysis

## Understanding the Output

### Score Ranges

- **90-100**: Exceptional candidates - interview immediately
- **80-89**: Strong candidates - high priority
- **70-79**: Good candidates - worth considering
- **60-69**: Decent matches - review if needed
- **Below 60**: Likely not a strong fit

### Hidden Gems

Pay special attention to the "Hidden Gems" section - these are candidates who:
- Were previously rejected
- Scored 70+ in the AI analysis
- May deserve a second look

In our testing, 20-40% of top candidates were hidden gems!

## Tips for Best Results

1. **Add Company Context**: Improves AI evaluation accuracy
2. **Review All Sections**: Don't just look at scores
3. **Check Data Quality**: AI notes when candidate data is incomplete
4. **Validate Top Picks**: AI is a tool to augment, not replace, human judgment

## Next Steps

- [Configuration Guide](configuration.md) - Advanced configuration options
- [API Setup](api-setup.md) - Detailed API configuration
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## Need Help?

- Check our [FAQ](faq.md)
- Open an [issue on GitHub](https://github.com/culstrup/hirescope/issues)
- Email us at contact@gsdat.work