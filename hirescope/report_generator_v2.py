"""
Enhanced report generation with better UX
Creates reports in organized output folder and optionally opens them
"""

import json
import csv
import os
import platform
import subprocess
from datetime import datetime
from typing import Dict, List


class ReportGeneratorV2:
    """Enhanced report generator with better file organization"""
    
    def __init__(self):
        # Create output directory if it doesn't exist
        self.output_dir = "analysis_results"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_report(self, results: List[Dict], job_name: str, 
                       num_top_candidates: int = 10, total_time: float = 0,
                       total_cost: float = 0, auto_open: bool = True) -> Dict[str, str]:
        """
        Generate comprehensive analysis report with better UX
        
        Args:
            results: List of candidate analysis results
            job_name: Name of the job position
            num_top_candidates: Number of top candidates to highlight
            total_time: Total analysis time in minutes
            total_cost: Total API cost
            auto_open: Whether to automatically open the report
            
        Returns:
            Dictionary with paths to generated files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_job_name = job_name.replace(' ', '_').replace('/', '_')
        
        # Create job-specific subfolder
        job_folder = os.path.join(self.output_dir, f"{safe_job_name}_{timestamp}")
        os.makedirs(job_folder, exist_ok=True)
        
        # Sort candidates by score
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
        # Generate all reports
        md_path = self._generate_markdown_report(
            sorted_results, job_name, safe_job_name, 
            num_top_candidates, total_time, total_cost, timestamp, job_folder
        )
        
        csv_path = self._generate_csv_summary(
            sorted_results[:num_top_candidates], safe_job_name, timestamp, job_folder
        )
        
        # Save full JSON results
        json_path = os.path.join(job_folder, f"full_results.json")
        with open(json_path, 'w') as f:
            json.dump({
                'job_name': job_name,
                'analysis_date': datetime.now().isoformat(),
                'total_candidates': len(results),
                'total_time_minutes': total_time,
                'total_cost_usd': total_cost,
                'results': results
            }, f, indent=2)
        
        # Create a quick summary file
        summary_path = self._generate_quick_summary(
            sorted_results[:5], job_name, total_time, total_cost, job_folder
        )
        
        # Print enhanced output
        print(f"\n✅ Reports saved to: {job_folder}/")
        print(f"\n📊 Quick Preview - Top 5 Candidates:")
        print("-" * 80)
        
        for i, candidate in enumerate(sorted_results[:5], 1):
            print(f"\n{i}. {candidate.get('name', 'Unknown')} - Score: {candidate.get('score', 0)}/100")
            print(f"   {candidate.get('summary', 'No summary')[:100]}...")
            gh_link = self._generate_greenhouse_link(
                candidate.get('candidate_id', ''),
                candidate.get('application_id', '')
            )
            print(f"   🔗 {gh_link}")
        
        print("\n" + "-" * 80)
        print(f"\n📁 All Files:")
        print(f"   📝 Report: {os.path.basename(md_path)}")
        print(f"   📊 Top {num_top_candidates} CSV: {os.path.basename(csv_path)}")
        print(f"   🗂️  Full Data: {os.path.basename(json_path)}")
        print(f"   ⚡ Quick Summary: {os.path.basename(summary_path)}")
        
        # Auto-open the report if requested
        if auto_open:
            self._open_file(md_path)
            print(f"\n📖 Opening report in your default viewer...")
        
        return {
            'markdown': md_path,
            'csv': csv_path,
            'json': json_path,
            'summary': summary_path,
            'output_folder': job_folder
        }
    
    def _generate_quick_summary(self, top_candidates: List[Dict], job_name: str,
                               total_time: float, total_cost: float, 
                               output_folder: str) -> str:
        """Generate a quick text summary for easy sharing"""
        
        summary = f"""CANDIDATE ANALYSIS SUMMARY
{job_name}
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Analysis Time: {total_time:.1f} minutes | Cost: ${total_cost:.2f}

TOP 5 CANDIDATES:

"""
        
        for i, candidate in enumerate(top_candidates, 1):
            gh_link = self._generate_greenhouse_link(
                candidate.get('candidate_id', ''),
                candidate.get('application_id', '')
            )
            
            summary += f"""{i}. {candidate.get('name', 'Unknown')} - Score: {candidate.get('score', 0)}/100
   Status: {candidate.get('status', 'Unknown')}
   Summary: {candidate.get('summary', 'No summary available')}
   Recommendation: {candidate.get('hire_recommendation', 'No recommendation')}
   Greenhouse: {gh_link}
   
"""
        
        # Save summary
        summary_path = os.path.join(output_folder, "QUICK_SUMMARY.txt")
        with open(summary_path, 'w') as f:
            f.write(summary)
            
        return summary_path
    
    def _open_file(self, filepath: str):
        """Open file in default application (cross-platform)"""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath], check=False)
            elif platform.system() == 'Windows':
                os.startfile(filepath)  # type: ignore[attr-defined]
            else:  # Linux
                subprocess.run(['xdg-open', filepath], check=False)
        except:
            # If auto-open fails, just continue
            pass
    
    def _generate_markdown_report(self, sorted_results: List[Dict], job_name: str,
                                 safe_job_name: str, num_top: int, 
                                 total_time: float, total_cost: float,
                                 timestamp: str, output_folder: str) -> str:
        """Generate detailed markdown report"""
        
        # [Previous markdown generation code remains the same]
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
        
        # Add top candidates with all details
        for i, candidate in enumerate(sorted_results[:num_top], 1):
            gh_link = self._generate_greenhouse_link(
                candidate.get('candidate_id', ''),
                candidate.get('application_id', '')
            )
            
            report += f"""### {i}. {candidate.get('name', 'Unknown')} - Score: {candidate.get('score', 0)}/100

**[View in Greenhouse]({gh_link})**  
**Applied**: {candidate.get('applied_at', 'N/A')[:10]} | **Status**: {candidate.get('status', 'Unknown')} | **Stage**: {candidate.get('current_stage', 'Unknown')}

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
            for candidate in hidden_gems[:10]:
                gh_link = self._generate_greenhouse_link(
                    candidate.get('candidate_id', ''),
                    candidate.get('application_id', '')
                )
                report += f"- **[{candidate.get('name', 'Unknown')}]({gh_link})** "
                report += f"(Score: {candidate.get('score', 0)}) - "
                report += f"{candidate.get('summary', 'No summary')[:100]}...\n"
        
        report += """
---

## 📋 Evaluation Methodology

Candidates were scored on a 0-100 scale based on:

1. **Skills & Experience Match** (40 points max)
2. **Achievements & Impact** (30 points max)
3. **Culture & Industry Fit** (20 points max)
4. **Growth Potential** (10 points max)

---

*Report generated by HireScope v1.0 - AI-powered candidate analysis for Greenhouse ATS*
"""
        
        # Save report
        filename = os.path.join(output_folder, f"Full_Report.md")
        with open(filename, 'w') as f:
            f.write(report)
            
        return filename
    
    def _generate_csv_summary(self, top_candidates: List[Dict], 
                             safe_job_name: str, timestamp: str,
                             output_folder: str) -> str:
        """Generate CSV summary of top candidates"""
        
        filename = os.path.join(output_folder, f"Top_Candidates.csv")
        
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
            return "No link available"