"""
Core candidate analysis engine for HireScope
Analyzes candidates from Greenhouse against job requirements using OpenAI
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from hirescope.greenhouse_api import GreenhouseClient
from hirescope.document_processor import DocumentProcessor
from hirescope.ai_scorer import AIScorer
from hirescope.report_generator_v2 import ReportGeneratorV2


class CandidateAnalyzer:
    """Main analysis engine that orchestrates the candidate evaluation process"""
    
    def __init__(self, greenhouse_key: str, openai_key: str):
        self.greenhouse = GreenhouseClient(greenhouse_key)
        self.doc_processor = DocumentProcessor()
        self.ai_scorer = AIScorer(openai_key)
        self.report_gen = ReportGeneratorV2()
        self.job_desc_cache = {}
        
    def analyze_job(self, job_id: int, company_context: str = "", 
                   num_top_candidates: int = 10, save_progress: bool = True) -> Dict:
        """
        Analyze all candidates for a specific job
        
        Args:
            job_id: Greenhouse job ID
            company_context: Additional context about company culture/values
            num_top_candidates: Number of top candidates to highlight
            save_progress: Whether to save progress checkpoints
            
        Returns:
            Dictionary with analysis results and report paths
        """
        start_time = datetime.now()
        
        # Get job details
        job_data = self.greenhouse.get_job(job_id)
        job_name = job_data['name']
        job_description = self._get_comprehensive_job_description(job_data)
        
        print(f"\n🎯 Analyzing: {job_name}")
        print(f"📄 Job context: {len(job_description)} characters")
        print("=" * 60)
        
        # Get all applications
        applications = self.greenhouse.get_applications(job_id)
        print(f"📊 Found {len(applications)} applications to analyze")
        
        # Analyze each candidate
        results = []
        total_cost = 0.0
        
        for i, app in enumerate(applications):
            # Progress tracking
            progress = (i + 1) / len(applications) * 100
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta_seconds = (len(applications) - i - 1) / rate if rate > 0 else 0
            
            print(f"\n📋 Candidate {i+1}/{len(applications)} ({progress:.1f}%)")
            print(f"   ⏱️  ETA: {eta_seconds/60:.1f} minutes")
            
            try:
                # Get candidate details
                candidate = self.greenhouse.get_candidate(app['candidate_id'])
                if not candidate:
                    continue
                    
                candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
                print(f"   👤 {candidate_name}")
                
                # Process attachments
                attachments_data = self._process_candidate_attachments(app, candidate_name)
                
                # Build candidate profile
                profile = self._build_candidate_profile(app, candidate, attachments_data)
                
                # Score with AI
                print(f"   🤖 Scoring with AI...")
                score_result = self.ai_scorer.score_candidate(
                    job_title=job_name,
                    job_description=job_description,
                    candidate_profile=profile,
                    company_context=company_context
                )
                
                # Add metadata
                score_result.update({
                    'candidate_id': candidate['id'],
                    'application_id': app['id'],
                    'name': candidate_name,
                    'applied_at': app.get('applied_at', ''),
                    'status': app.get('status', 'active'),
                    'current_stage': app.get('current_stage', {}).get('name', 'Unknown')
                })
                
                results.append(score_result)
                total_cost += score_result.get('cost', 0)
                
                # Save progress checkpoint
                if save_progress and (i + 1) % 10 == 0:
                    self._save_progress(job_name, results, i + 1)
                    
            except Exception as e:
                print(f"   ❌ Error processing candidate: {str(e)}")
                continue
        
        # Generate final report
        print("\n📊 Generating analysis report...")
        
        report_paths = self.report_gen.generate_report(
            results=results,
            job_name=job_name,
            num_top_candidates=num_top_candidates,
            total_time=(datetime.now() - start_time).total_seconds() / 60,
            total_cost=total_cost
        )
        
        return {
            'job_name': job_name,
            'total_candidates': len(results),
            'analysis_time_minutes': (datetime.now() - start_time).total_seconds() / 60,
            'total_cost': total_cost,
            'report_paths': report_paths,
            'top_candidate': sorted(results, key=lambda x: x['score'], reverse=True)[0] if results else None
        }
    
    def get_available_jobs(self) -> List[Dict]:
        """Get all jobs with applications available for analysis"""
        return self.greenhouse.get_jobs_with_applications()
    
    def _get_comprehensive_job_description(self, job_data: Dict) -> str:
        """Extract comprehensive job description from all available sources"""
        job_id = job_data['id']
        
        # Check cache
        if job_id in self.job_desc_cache:
            return self.job_desc_cache[job_id]
            
        # Try API notes field first
        if job_data.get('notes') and len(job_data['notes']) > 100:
            return job_data['notes']
            
        # Build from metadata and custom fields
        desc_parts = [f"Position: {job_data['name']}\n"]
        
        # Add department and location
        if job_data.get('departments'):
            desc_parts.append(f"Department: {job_data['departments'][0]['name']}")
        if job_data.get('offices'):
            desc_parts.append(f"Location: {job_data['offices'][0]['name']}")
            
        # Add custom fields
        if job_data.get('keyed_custom_fields'):
            cf = job_data['keyed_custom_fields']
            desc_parts.append("\nJob Details:")
            
            for field, value in cf.items():
                if value:
                    # Format field name
                    field_name = field.replace('_', ' ').title()
                    if isinstance(value, dict) and 'value' in value:
                        desc_parts.append(f"- {field_name}: ${value['value']} {value.get('unit', '')}")
                    else:
                        desc_parts.append(f"- {field_name}: {value}")
        
        # Try to get requirements from application questions
        try:
            sample_app = self.greenhouse.get_applications(job_id, limit=1)
            if sample_app and sample_app[0].get('answers'):
                requirements = []
                for answer in sample_app[0]['answers']:
                    question = answer.get('question', '')
                    if any(term in question.lower() for term in ['experience', 'years', 'certification', 'skill']):
                        requirements.append(f"- {question}")
                        
                if requirements:
                    desc_parts.append("\nRequirements (from application):")
                    desc_parts.extend(requirements)
        except:
            pass
            
        description = "\n".join(desc_parts)
        self.job_desc_cache[job_id] = description
        return description
    
    def _process_candidate_attachments(self, app: Dict, candidate_name: str) -> Dict:
        """Process all candidate attachments"""
        print(f"   📄 Processing attachments...")
        
        attachments_data = {
            'resume_text': '',
            'cover_letter_text': '',
            'other_attachments': []
        }
        
        for attachment in app.get('attachments', []):
            try:
                # Download attachment
                content = self.greenhouse.download_attachment(attachment['url'])
                if not content:
                    continue
                    
                # Extract text based on type
                filename = attachment.get('filename', '')
                attachment_type = attachment.get('type', 'document')
                
                text = self.doc_processor.extract_text(content, filename)
                
                if 'resume' in attachment_type.lower():
                    attachments_data['resume_text'] = text
                elif 'cover' in attachment_type.lower():
                    attachments_data['cover_letter_text'] = text
                else:
                    attachments_data['other_attachments'].append({
                        'type': attachment_type,
                        'filename': filename,
                        'text': text[:1000]  # First 1000 chars
                    })
                    
            except Exception as e:
                print(f"      ⚠️  Failed to process {attachment.get('filename', 'attachment')}: {str(e)}")
                
        return attachments_data
    
    def _build_candidate_profile(self, app: Dict, candidate: Dict, attachments_data: Dict) -> str:
        """Build comprehensive candidate profile"""
        name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
        email = candidate.get('email_addresses', [{}])[0].get('value', 'N/A') if candidate.get('email_addresses') else 'N/A'
        
        # Process application answers
        answers = []
        for answer in app.get('answers', []):
            question = answer.get('question', '')
            response = answer.get('answer', '')
            if response:
                answers.append(f"{question}: {response}")
                
        profile = f"""
CANDIDATE: {name}
EMAIL: {email}
APPLIED: {app.get('applied_at', 'N/A')[:10]}

APPLICATION RESPONSES:
{chr(10).join(answers) if answers else 'No responses provided'}

RESUME:
{attachments_data['resume_text'] if attachments_data['resume_text'] else '[No resume available]'}

COVER LETTER:
{attachments_data['cover_letter_text'] if attachments_data['cover_letter_text'] else '[No cover letter]'}
"""
        
        return profile
    
    def _save_progress(self, job_name: str, results: List[Dict], count: int):
        """Save progress checkpoint"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"progress_{job_name.replace(' ', '_')}_{count}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'job_name': job_name,
                'progress_count': count,
                'timestamp': timestamp,
                'results': results
            }, f, indent=2)
            
        print(f"   💾 Progress saved: {filename}")