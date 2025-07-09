#!/usr/bin/env python3
"""
HireScope - AI-powered candidate analysis for Greenhouse ATS
Copyright (c) 2025 GSD at Work LLC

Analyze hundreds of candidates in minutes to find the best fit
and discover hidden gems among previously rejected applicants.
"""

import os
import sys

from dotenv import load_dotenv

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "hirescope"))

from analyzer import CandidateAnalyzer


def print_banner():
    """Display welcome banner"""
    print(
        """
╔════════════════════════════════════════════════════╗
║           HIRESCOPE v1.0 🎯                       ║
║   AI-Powered Candidate Analysis for Greenhouse    ║
║                                                    ║
║   Analyze hundreds of applications in minutes      ║
║   Find hidden gems in rejected candidates          ║
║                                                    ║
║        © 2025 GSD at Work LLC                     ║
║        https://gsdat.work                         ║
╚════════════════════════════════════════════════════╝
    """
    )


def load_config():
    """Load configuration from environment"""
    load_dotenv()

    greenhouse_key = os.getenv("GREENHOUSE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not greenhouse_key:
        print("❌ ERROR: GREENHOUSE_API_KEY not found!")
        print("Please add it to your .env file")
        print("\nGet your API key from:")
        print("Greenhouse > Configure > Dev Center > API Credential Management")
        sys.exit(1)

    if not openai_key:
        print("❌ ERROR: OPENAI_API_KEY not found!")
        print("Please add it to your .env file")
        print("\nGet your API key from:")
        print("https://platform.openai.com/api-keys")
        sys.exit(1)

    return greenhouse_key, openai_key


def display_jobs_menu(jobs):
    """Display available jobs for analysis"""
    print(f"\n🎯 AVAILABLE JOBS FOR ANALYSIS ({len(jobs)} total)")
    print("=" * 80)
    print(f"{'#':<4} {'Status':<8} {'Job Title':<40} {'Department':<20} {'Created'}")
    print("-" * 80)

    for i, job in enumerate(jobs, 1):
        status_icon = "🟢" if job["status"] == "open" else "🔴"
        status_text = job["status"].upper()
        print(
            f"{i:<4} {status_icon} {status_text:<6} {job['name'][:40]:<40} {job['department'][:20]:<20} {job['created_at']}"
        )

    print("-" * 80)
    print("\n💡 In real-world use, 20-40% of top candidates are often hidden gems")
    print("   (previously rejected applicants who deserve a second look)")


def get_user_selections():
    """Get analysis parameters from user"""

    # Job selection
    while True:
        try:
            choice = input(
                "\n📍 Enter job number to analyze (or 'q' to quit): "
            ).strip()

            if choice.lower() == "q":
                print("\n👋 Thanks for using HireScope!")
                sys.exit(0)

            job_index = int(choice) - 1
            if job_index < 0:
                raise ValueError()

            break

        except (ValueError, IndexError):
            print("❌ Invalid selection. Please try again.")

    # Number of top candidates
    while True:
        try:
            num_str = input(
                "\nHow many top candidates to identify? (5-20, default=10): "
            ).strip()
            num_top = int(num_str) if num_str else 10

            if 5 <= num_top <= 20:
                break
            else:
                print("❌ Please enter a number between 5 and 20")

        except ValueError:
            print("❌ Please enter a valid number")

    # Company context
    print("\n📝 Company Context (optional)")
    print("Describe your company culture, values, or specific requirements.")
    print("Example: 'Fast-growing startup, remote-first, values autonomy'")
    print("Press Enter to skip: ", end="")
    company_context = input().strip()

    return job_index, num_top, company_context


def confirm_analysis(job, num_top, company_context):
    """Confirm analysis parameters with user"""
    print("\n✅ READY TO ANALYZE")
    print(f"   Job: {job['name']}")
    print(f"   Department: {job['department']}")
    print(f"   Status: {job['status']}")
    print(f"   Top candidates to find: {num_top}")
    print(f"   Company context: {'Yes' if company_context else 'No'}")

    print("\n⚠️  This will analyze ALL candidates for this job.")
    print(
        "The analysis may take several minutes depending on the number of candidates."
    )

    response = input("\nProceed with analysis? (y/n): ").strip().lower()
    return response == "y"


def main():
    """Main CLI workflow"""
    print_banner()

    # Load configuration
    print("🔧 Loading configuration...")
    greenhouse_key, openai_key = load_config()

    # Initialize analyzer
    analyzer = CandidateAnalyzer(greenhouse_key, openai_key)

    # Get available jobs
    print("\n📋 Fetching jobs from Greenhouse...")
    jobs = analyzer.get_available_jobs()

    if not jobs:
        print("\n❌ No jobs with applications found!")
        print("Make sure you have jobs with at least one application in Greenhouse.")
        sys.exit(1)

    # Display jobs menu
    display_jobs_menu(jobs)

    # Get user selections
    job_index, num_top, company_context = get_user_selections()
    selected_job = jobs[job_index]

    # Confirm before proceeding
    if not confirm_analysis(selected_job, num_top, company_context):
        print("\n❌ Analysis cancelled")
        sys.exit(0)

    # Run analysis
    print("\n🚀 Starting analysis...")
    print(
        "You can monitor progress below. The analysis will save checkpoints automatically.\n"
    )

    try:
        result = analyzer.analyze_job(
            job_id=selected_job["id"],
            company_context=company_context,
            num_top_candidates=num_top,
            save_progress=True,
        )

        # Display results summary
        print("\n" + "=" * 60)
        print("✨ ANALYSIS COMPLETE!")
        print("=" * 60)
        print("\n📊 Results Summary:")
        print(f"   Job: {result['job_name']}")
        print(f"   Candidates analyzed: {result['total_candidates']}")
        print(f"   Time taken: {result['analysis_time_minutes']:.1f} minutes")
        print(f"   Total cost: ${result['total_cost']:.2f}")

        if result["top_candidate"]:
            print("\n🏆 Top Candidate:")
            print(f"   Name: {result['top_candidate']['name']}")
            print(f"   Score: {result['top_candidate']['score']}/100")
            print(f"   Summary: {result['top_candidate'].get('summary', 'N/A')}")

        print("\n📁 Output Files:")
        for file_type, path in result["report_paths"].items():
            print(f"   {file_type.capitalize()}: {path}")

        print(
            "\n✅ Analysis complete! Review the markdown report for detailed insights."
        )
        print("\n💡 Don't forget to check the 'Hidden Gems' section - these are")
        print("   high-scoring candidates who were previously rejected!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        print("Progress has been saved. You can resume by running the analysis again.")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("- Check your API keys are valid")
        print("- Ensure you have the necessary Greenhouse permissions")
        print("- Check your internet connection")
        print("- Review the error message above")

        import traceback

        print("\nDetailed error:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
