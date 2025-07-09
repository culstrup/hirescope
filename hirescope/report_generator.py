"""
Report generation for candidate analysis results
Creates markdown reports and CSV summaries
"""

import json
import csv
from datetime import datetime
from typing import Dict, List


class ReportGenerator:
    """Generates analysis reports in various formats"""
    
    def generate_report(self, results: List[Dict], job_name: str, 
                       num_top_candidates: int = 10, total_time: float = 0,
                       total_cost: float = 0) -> Dict[str, str]:
        """
        Generate comprehensive analysis report
        
        Args:
            results: List of candidate analysis results
            job_name: Name of the job position
            num_top_candidates: Number of top candidates to highlight
            total_time: Total analysis time in minutes
            total_cost: Total API cost
            
        Returns:
            Dictionary with paths to generated files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_job_name = job_name.replace(' ', '_').replace('/', '_')
        
        # Sort candidates by score
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
        # Generate markdown report
        md_path = self._generate_markdown_report(
            sorted_results, job_name, safe_job_name, 
            num_top_candidates, total_time, total_cost, timestamp
        )
        
        # Generate CSV summary
        csv_path = self._generate_csv_summary(
            sorted_results[:num_top_candidates], safe_job_name, timestamp
        )
        
        # Save full JSON results
        json_path = f"RESULTS_{safe_job_name}_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump({
                'job_name': job_name,
                'analysis_date': datetime.now().isoformat(),
                'total_candidates': len(results),
                'total_time_minutes': total_time,
                'total_cost_usd': total_cost,
                'results': results
            }, f, indent=2)
            
        print(f"\n✅ Reports generated:")
        print(f"   📄 Markdown: {md_path}")
        print(f"   📊 CSV: {csv_path}")
        print(f"   🗂️  JSON: {json_path}")
        
        return {
            'markdown': md_path,
            'csv': csv_path,
            'json': json_path
        }
        
    def _generate_markdown_report(self, sorted_results: List[Dict], job_name: str,
                                 safe_job_name: str, num_top: int, 
                                 total_time: float, total_cost: float,
                                 timestamp: str) -> str:
        """Generate detailed markdown report"""
        
        report = f"""# 🎯 Candidate Analysis Report: {job_name}

**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  
**Total Candidates Analyzed**: {len(sorted_results)}  
**Analysis Time**: {total_time:.1f} minutes  
**Total Cost**: ${total_cost:.2f}  
**Powered by**: OpenAI o3 with comprehensive scoring

---

## 📊 Score Distribution

"""
        # Add score distribution
        score_ranges = {
            '90-100': 0, '80-89': 0, '70-79': 0, 
            '60-69': 0, '50-59': 0, 'Below 50': 0
        }
        
        for candidate in sorted_results:
            score = candidate.get('score', 0)
            if score >= 90:
                score_ranges['90-100'] += 1
            elif score >= 80:
                score_ranges['80-89'] += 1
            elif score >= 70:
                score_ranges['70-79'] += 1
            elif score >= 60:
                score_ranges['60-69'] += 1
            elif score >= 50:
                score_ranges['50-59'] += 1
            else:
                score_ranges['Below 50'] += 1
                
        for range_name, count in score_ranges.items():
            if count > 0:
                report += f"- **{range_name}**: {count} candidates\n"
                
        report += f"\n---\n\n## 🏆 Top {num_top} Candidates\n\n"
        
        # Add top candidates
        for i, candidate in enumerate(sorted_results[:num_top], 1):
            # Generate Greenhouse link
            gh_link = self._generate_greenhouse_link(
                candidate.get('candidate_id', ''),
                candidate.get('application_id', '')
            )
            
            report += f"""### {i}. {candidate.get('name', 'Unknown')} - Score: {candidate.get('score', 0)}/100

**Greenhouse Profile**: [{candidate.get('name', 'Unknown')}]({gh_link})  
**Applied**: {candidate.get('applied_at', 'N/A')[:10]}  
**Current Status**: {candidate.get('status', 'Unknown')}  
**Stage**: {candidate.get('current_stage', 'Unknown')}

**Executive Summary**: {candidate.get('summary', 'No summary available')}

**Key Strengths**:
"""
            for strength in candidate.get('key_strengths', []):
                report += f"- {strength}\n"
                
            if candidate.get('notable_achievements'):
                report += "\n**Notable Achievements**:\n"
                for achievement in candidate['notable_achievements']:
                    report += f"- {achievement}\n"
                    
            report += f"\n**Culture Fit**: {candidate.get('culture_fit', 'Not assessed')}\n"
            
            if candidate.get('concerns'):
                report += "\n**Potential Concerns**:\n"
                for concern in candidate['concerns']:
                    report += f"- {concern}\n"
                    
            report += f"\n**Hiring Recommendation**: {candidate.get('hire_recommendation', 'No recommendation')}\n"
            report += f"\n**Data Quality**: {candidate.get('data_quality', 'Unknown')}\n"
            report += "\n---\n\n"
            
        # Add hidden gems section
        hidden_gems = [
            c for c in sorted_results 
            if c.get('status') == 'rejected' and c.get('score', 0) >= 70
        ]
        
        if hidden_gems:
            report += f"""## 💎 Hidden Gems (High-Scoring Rejected Candidates)

Found **{len(hidden_gems)}** previously rejected candidates with scores ≥ 70:

"""
            for candidate in hidden_gems[:10]:  # Top 10 hidden gems
                gh_link = self._generate_greenhouse_link(
                    candidate.get('candidate_id', ''),
                    candidate.get('application_id', '')
                )
                report += f"- **[{candidate.get('name', 'Unknown')}]({gh_link})** "
                report += f"(Score: {candidate.get('score', 0)}) - "
                report += f"{candidate.get('summary', 'No summary')[:100]}...\n"
                
        # Add methodology section
        report += """
---

## 📋 Evaluation Methodology

Candidates were scored on a 0-100 scale based on:

1. **Skills & Experience Match** (40 points max)
   - Technical skills alignment
   - Years and relevance of experience
   - Industry background

2. **Achievements & Impact** (30 points max)
   - Quantifiable accomplishments
   - Leadership and initiative
   - Problem-solving examples

3. **Culture & Industry Fit** (20 points max)
   - Alignment with company values
   - Industry knowledge
   - Communication style

4. **Growth Potential** (10 points max)
   - Learning agility
   - Career trajectory
   - Soft skills

---

*Report generated by HireScope v1.0 - AI-powered candidate analysis for Greenhouse ATS*  
*© 2025 GSD at Work LLC - https://gsdat.work*
"""
        
        # Save report
        filename = f"REPORT_{safe_job_name}_{timestamp}.md"
        with open(filename, 'w') as f:
            f.write(report)
            
        return filename
        
    def _generate_csv_summary(self, top_candidates: List[Dict], 
                             safe_job_name: str, timestamp: str) -> str:
        """Generate CSV summary of top candidates"""
        
        filename = f"TOP_CANDIDATES_{safe_job_name}_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Rank', 'Name', 'Score', 'Status', 'Applied Date',
                'Greenhouse Link', 'Summary', 'Recommendation'
            ])
            
            # Data rows
            for i, candidate in enumerate(top_candidates, 1):
                gh_link = self._generate_greenhouse_link(
                    candidate.get('candidate_id', ''),
                    candidate.get('application_id', '')
                )
                
                writer.writerow([
                    i,
                    candidate.get('name', 'Unknown'),
                    candidate.get('score', 0),
                    candidate.get('status', 'Unknown'),
                    candidate.get('applied_at', '')[:10],
                    gh_link,
                    candidate.get('summary', ''),
                    candidate.get('hire_recommendation', '')
                ])
                
        return filename
        
    def _generate_greenhouse_link(self, candidate_id: str, application_id: str) -> str:
        """Generate direct Greenhouse link to candidate profile"""
        if candidate_id and application_id:
            return f"https://app8.greenhouse.io/people/{candidate_id}/applications/{application_id}"
        else:
            return "#"