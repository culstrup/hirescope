# 🎯 HireScope - AI-Powered Candidate Analysis for Greenhouse ATS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Analyze hundreds of job applications in minutes, not hours.** HireScope uses OpenAI's advanced reasoning models to evaluate every candidate in your Greenhouse ATS, helping recruiters focus their limited attention on the best fits.

## 🌟 Key Discovery: Hidden Gems

In real-world testing across multiple roles, **20-40% of our top AI-recommended candidates were "hidden gems"** - previously rejected applicants who deserved a second look. Don't let great talent slip through the cracks.

## 📋 Sample Output

Want to see what HireScope produces? Check out our **[example output files](examples/)** to see real analysis results:

- 📄 **[Full Analysis Report](examples/SAMPLE_REPORT_Senior_Software_Engineer.md)** - Complete markdown report showing AI evaluations, hidden gems, and recommendations
- 📊 **[Top Candidates CSV](examples/SAMPLE_TOP_CANDIDATES_Senior_Software_Engineer.csv)** - Quick reference export for hiring managers
- 💡 **Key Insight**: In our sample, the #1 highest-scoring candidate (92/100) had been rejected after phone screen!

## ✨ Features

- **Comprehensive Analysis**: Evaluates ALL candidates, including rejected ones
- **AI-Powered Scoring**: Uses OpenAI's o3 model for detailed 0-100 scoring with reasoning
- **Complete Data Extraction**: Processes resumes (PDF/DOCX), cover letters, and application responses
- **Direct Greenhouse Integration**: One-click links to candidate profiles
- **Professional Reports**: Markdown reports, CSV summaries, and JSON data export
- **Cost Effective**: ~$0.02 per candidate (analyze 1,000 candidates for ~$20)
- **Progress Tracking**: Automatic checkpointing for large analysis jobs

## 📊 Real Results

> "We analyzed 1,049 historical candidates and found 176 hidden gems - high-quality candidates who had been rejected but scored 70+ in our AI evaluation."

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Greenhouse account with API access
- OpenAI API key (with o3 model access)

### Installation

```bash
# Clone the repository
git clone https://github.com/culstrup/hirescope.git
cd hirescope

# Run setup script
./setup.sh

# Add your API keys
nano .env
```

### Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run the analyzer
python hirescope.py
```

The tool will:
1. Connect to your Greenhouse account
2. Show all jobs with applications
3. Let you select a job to analyze
4. Evaluate every candidate using AI
5. Generate comprehensive reports with top candidates and hidden gems

## 📈 How It Works

1. **Data Collection**: Fetches all candidates and their attachments from Greenhouse
2. **Document Processing**: Extracts text from resumes and cover letters
3. **AI Evaluation**: Sends comprehensive profiles to OpenAI for scoring
4. **Smart Ranking**: Scores candidates on skills, experience, culture fit, and potential
5. **Hidden Gem Detection**: Identifies high-scoring rejected candidates

### Scoring Criteria (0-100 scale)

- **Skills & Experience Match** (40 points)
- **Achievements & Impact** (30 points)
- **Culture & Industry Fit** (20 points)
- **Growth Potential** (10 points)

## 📁 Output

HireScope generates three types of output:

1. **Markdown Report** - Comprehensive analysis with direct Greenhouse links
2. **CSV Summary** - Top candidates for easy sharing
3. **JSON Data** - Complete results for further analysis

## 🔧 Configuration

### API Keys

Add to your `.env` file:

```env
# Greenhouse Harvest API Key
GREENHOUSE_API_KEY=your_key_here

# OpenAI API Key
OPENAI_API_KEY=sk-your_key_here
```

### Greenhouse Permissions

Your API key needs:
- Applications (GET)
- Candidates (GET)
- Jobs (GET)

## 💰 Cost Estimation

- 100 candidates ≈ $2
- 500 candidates ≈ $10
- 1,000 candidates ≈ $20

Cost varies based on resume length and current API pricing.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About GSD at Work LLC

[GSD at Work LLC](https://gsdat.work) helps companies leverage AI to solve real business problems. HireScope is our contribution to making recruiting more efficient and inclusive.

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/culstrup/hirescope/issues)
- **Discussions**: [GitHub Discussions](https://github.com/culstrup/hirescope/discussions)
- **Email**: christian@gsdat.work

## 🚀 Roadmap

- [ ] Support for additional file formats (RTF, TXT)
- [ ] Bulk analysis for multiple jobs
- [ ] Integration with other ATS platforms
- [ ] Web-based interface
- [ ] Team collaboration features

---

**Built with ❤️ by [GSD at Work LLC](https://gsdat.work)**

*Making recruiting more human with AI*
