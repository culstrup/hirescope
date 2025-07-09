"""
AI-powered candidate scoring using OpenAI
Uses o3 model for comprehensive evaluation
"""

import json
import time
import urllib.error
import urllib.request
from typing import Dict


class AIScorer:
    """Scores candidates using OpenAI's o3 model"""

    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "o3"
        self.max_retries = 3

    def score_candidate(
        self,
        job_title: str,
        job_description: str,
        candidate_profile: str,
        company_context: str = "",
    ) -> Dict:
        """
        Score a candidate using AI

        Args:
            job_title: Title of the position
            job_description: Full job requirements and description
            candidate_profile: Complete candidate information
            company_context: Optional company culture/values context

        Returns:
            Dictionary with score, analysis, and recommendations
        """

        # Build prompt
        context_section = (
            f"\nCOMPANY CONTEXT:\n{company_context}\n" if company_context else ""
        )

        prompt = f"""Evaluate this {job_title} candidate.

JOB REQUIREMENTS:
{job_description}
{context_section}
CANDIDATE PROFILE:
{candidate_profile}

Provide comprehensive evaluation based on:
- Skills and experience match (40 points max)
- Achievements and quantifiable impact (30 points max)  
- Industry/culture fit (20 points max)
- Growth potential and soft skills (10 points max)

Return JSON with:
{{
    "score": <0-100>,
    "summary": "2-3 sentence executive summary",
    "key_strengths": ["top 3 relevant qualifications"],
    "concerns": ["any gaps or concerns"],
    "hire_recommendation": "Strong Yes/Yes/Maybe/No with brief rationale",
    "notable_achievements": ["specific accomplishments if found"],
    "culture_fit": "assessment of fit with company culture",
    "data_quality": "completeness of candidate information"
}}"""

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "developer",
                    "content": "You are an expert recruiter and talent evaluator. Provide objective, thorough assessments based on all available information. Be constructive but honest about gaps or concerns.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_completion_tokens": 2000,
            "reasoning_effort": "medium",
            "response_format": {"type": "json_object"},
        }

        # Make API request with retries
        for attempt in range(self.max_retries):
            try:
                request = urllib.request.Request(
                    self.api_url, data=json.dumps(data).encode("utf-8"), headers=headers
                )

                with urllib.request.urlopen(request) as response:
                    result = json.loads(response.read().decode())

                # Extract the evaluation
                evaluation = json.loads(result["choices"][0]["message"]["content"])

                # Add cost tracking
                usage = result.get("usage", {})
                evaluation["cost"] = self._calculate_cost(usage)

                return evaluation

            except urllib.error.HTTPError as e:
                if e.code == 429:  # Rate limited
                    wait_time = 30 * (attempt + 1)
                    print(f"      ⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = e.read().decode() if e.fp else str(e)
                    print(f"      ❌ API error: {error_msg[:200]}")

            except json.JSONDecodeError:
                print("      ⚠️  Invalid JSON response, retrying...")

            except Exception as e:
                print(f"      ❌ Unexpected error: {str(e)[:200]}")

        # Return default score if all retries fail
        return {
            "score": 0,
            "summary": "Scoring failed due to technical issues",
            "key_strengths": [],
            "concerns": ["Unable to complete AI evaluation"],
            "hire_recommendation": "Unable to assess",
            "error": True,
            "cost": 0,
        }

    def _calculate_cost(self, usage: Dict) -> float:
        """Calculate API usage cost"""
        # o3 pricing (as of 2024)
        # These are example rates - update with actual pricing
        input_cost_per_1k = 0.015  # $15 per 1M tokens
        output_cost_per_1k = 0.060  # $60 per 1M tokens
        reasoning_cost_per_1k = 0.060  # Same as output

        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        reasoning_tokens = usage.get("reasoning_tokens", 0)

        cost = (
            (input_tokens / 1000) * input_cost_per_1k
            + (output_tokens / 1000) * output_cost_per_1k
            + (reasoning_tokens / 1000) * reasoning_cost_per_1k
        )

        return round(cost, 4)
