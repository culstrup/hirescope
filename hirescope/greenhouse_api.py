"""
Greenhouse Harvest API client
Handles all interactions with Greenhouse API
"""

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional


class GreenhouseClient:
    """Client for Greenhouse Harvest API v1"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.credentials = base64.b64encode(f"{api_key}:".encode()).decode()
        self.base_url = "https://harvest.greenhouse.io/v1"

    def _make_request(self, endpoint: str, method: str = "GET") -> Dict:
        """Make authenticated request to Greenhouse API"""
        url = f"{self.base_url}/{endpoint}"
        request = urllib.request.Request(url)
        request.add_header("Authorization", f"Basic {self.credentials}")

        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                print("   ⏳ Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, method)
            elif e.code == 403:
                raise Exception(
                    f"Permission denied. Check API key permissions for: {endpoint}"
                ) from e
            else:
                raise Exception(f"API error {e.code}: {e.reason}") from e

    def get_job(self, job_id: int) -> Dict:
        """Get job details including all metadata"""
        return self._make_request(f"jobs/{job_id}")

    def get_jobs_with_applications(self) -> List[Dict]:
        """Get all jobs that have applications to analyze"""
        all_jobs = []
        page = 1

        print("📋 Fetching available jobs...")

        while True:
            try:
                jobs = self._make_request(f"jobs?per_page=100&page={page}")
                if not jobs:
                    break

                # Check each job for applications
                for job in jobs:
                    try:
                        # Quick check if job has applications
                        apps = self._make_request(
                            f"applications?job_id={job['id']}&per_page=1"
                        )
                        if apps:
                            all_jobs.append(
                                {
                                    "id": job["id"],
                                    "name": job["name"],
                                    "status": job["status"],
                                    "department": job.get("departments", [{}])[0].get(
                                        "name", "N/A"
                                    ),
                                    "created_at": job.get("created_at", "")[:10],
                                    "application_count": len(
                                        apps
                                    ),  # This is just 1, but indicates presence
                                }
                            )
                    except Exception:
                        continue

                page += 1

            except Exception:
                break

        return sorted(all_jobs, key=lambda x: x["created_at"], reverse=True)

    def get_applications(self, job_id: int, limit: Optional[int] = None) -> List[Dict]:
        """Get all applications for a job"""
        applications: List[Dict] = []
        page = 1

        while True:
            try:
                apps = self._make_request(
                    f"applications?job_id={job_id}&per_page=100&page={page}"
                )
                if not apps:
                    break

                applications.extend(apps)

                if limit and len(applications) >= limit:
                    return applications[:limit]

                page += 1

            except Exception as e:
                print(f"   ⚠️  Error fetching applications page {page}: {e}")
                break

        return applications

    def get_candidate(self, candidate_id: int) -> Optional[Dict]:
        """Get candidate details"""
        try:
            return self._make_request(f"candidates/{candidate_id}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch candidate {candidate_id}: {e}")
            return None

    def download_attachment(self, url: str) -> Optional[bytes]:
        """Download attachment from S3 URL"""
        try:
            with urllib.request.urlopen(url) as response:
                return response.read()
        except Exception as e:
            print(f"      ⚠️  Download failed: {e}")
            return None
