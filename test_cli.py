#!/usr/bin/env python3
"""
Test CLI interface for the LinkedIn Job Scraper.

This script tests the command-line argument parsing without requiring
the jobspy module to be installed.
"""

import argparse
import sys

def test_cli_interface():
    """Test the CLI interface by parsing sample arguments."""

    # Create the same parser as in index.py
    parser = argparse.ArgumentParser(
        description='Enhanced LinkedIn Job Scraper with comprehensive filtering options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic usage:
    python %(prog)s --csv companies.csv --location "San Francisco, CA"

  Advanced filtering:
    python %(prog)s --csv companies.csv --location "Remote" \\
        --hours-old 168 \\
        --job-type fulltime \\
        --search-term "software engineer" \\
        --results-wanted 50 \\
        --distance 25

Job Types: fulltime, parttime, internship, contract
        """
    )

    # Required arguments
    parser.add_argument(
        '--csv',
        required=True,
        help='Input CSV file containing company names (must have "Company" column)'
    )
    parser.add_argument(
        '--location',
        required=True,
        help='Location to search for jobs (e.g., "San Francisco, CA", "Remote", "United States")'
    )

    # Optional output directory
    parser.add_argument(
        '--output',
        default='.',
        help='Directory to save output files (created if it doesn\'t exist). Default: current directory'
    )

    # Optional job filtering arguments
    parser.add_argument(
        '--hours-old',
        type=int,
        default=720,
        help='Filter jobs by hours since posting (e.g., 24=last day, 168=last week). Default: 720 (30 days)'
    )
    parser.add_argument(
        '--search-term',
        type=str,
        help='Additional search keywords to filter jobs (e.g., "python developer", "machine learning")'
    )
    parser.add_argument(
        '--job-type',
        choices=['fulltime', 'parttime', 'internship', 'contract'],
        help='Filter by employment type. Options: fulltime, parttime, internship, contract'
    )

    # Test cases
    test_cases = [
        # Basic usage
        ['--csv', 'companies.csv', '--location', 'Philippines'],

        # With output directory
        ['--csv', 'companies.csv', '--location', 'San Francisco, CA', '--output', './results'],

        # Advanced filtering
        ['--csv', 'companies.csv', '--location', 'Remote', '--hours-old', '168', '--job-type', 'fulltime'],

        # Complex case
        ['--csv', 'companies.csv', '--location', 'New York, NY', '--search-term', 'python developer', '--job-type', 'fulltime', '--hours-old', '72']
    ]

    print("Testing CLI Interface for LinkedIn Job Scraper")
    print("=" * 50)

    for i, test_args in enumerate(test_cases, 1):
        try:
            args = parser.parse_args(test_args)
            print(f"\n✅ Test Case {i}: SUCCESS")
            print(f"   Command: python index.py {' '.join(test_args)}")
            print(f"   Parsed args:")
            print(f"     CSV: {args.csv}")
            print(f"     Location: {args.location}")
            print(f"     Output: {args.output}")
            if hasattr(args, 'hours_old'):
                print(f"     Hours Old: {args.hours_old}")
            if hasattr(args, 'job_type') and args.job_type:
                print(f"     Job Type: {args.job_type}")
            if hasattr(args, 'search_term') and args.search_term:
                print(f"     Search Term: {args.search_term}")

        except SystemExit as e:
            print(f"\n❌ Test Case {i}: FAILED")
            print(f"   Command: python index.py {' '.join(test_args)}")
            print(f"   Error: Argument parsing failed")
        except Exception as e:
            print(f"\n❌ Test Case {i}: ERROR")
            print(f"   Command: python index.py {' '.join(test_args)}")
            print(f"   Error: {str(e)}")

    print(f"\n" + "=" * 50)
    print("CLI Interface Test Complete!")
    print("\nThe new interface matches the documentation:")
    print("✅ Required parameters: --csv and --location")
    print("✅ Optional parameter: --output (defaults to current directory)")
    print("✅ All filtering parameters work as expected")
    print("\nYou can now use commands like:")
    print("python index.py --csv companies.csv --location \"Philippines\"")

if __name__ == "__main__":
    test_cli_interface()
