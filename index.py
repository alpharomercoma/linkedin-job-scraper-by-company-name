"""
Enhanced LinkedIn Job Scraper with Comprehensive Parameters

This module provides a complete solution for scraping LinkedIn job postings from multiple
companies using the python-jobspy library. It includes advanced filtering options,
robust error handling, batch processing capabilities, and detailed logging.

Key Features:
    - Multi-company batch processing from CSV files
    - Advanced job filtering (time, type, location, keywords)
    - Comprehensive error handling and recovery
    - Progress tracking and detailed logging
    - Structured output with separate error/empty result files
    - Command-line interface with extensive parameter support
    - Fallback company name support for better job discovery

Dependencies:
    - python-jobspy: Core job scraping library
    - pandas: Data manipulation and CSV handling
    - requests: HTTP requests for LinkedIn company ID lookup
    - argparse: Command-line argument parsing
    - logging: Comprehensive logging support

Installation:
    pip install python-jobspy pandas requests

Usage Examples:
    Basic usage:
        python index.py companies.csv "San Francisco, CA" ./output

    Advanced filtering:
        python index.py companies.csv "Remote" ./output \\
            --hours-old 168 \\
            --job-type fulltime \\
            --search-term "software engineer" \\
            --results-wanted 50 \\
            --distance 25

    Batch processing:
        python index.py companies.csv "New York, NY" ./output \\
            --start 0 --end 99 \\
            --fetch-description \\
            --job-type internship

Input CSV Format:
    Required columns:
        - Company: Primary company name for job search
    Optional columns:
        - Company Name for Emails: Alternative company name used as fallback

Output Files:
    - jobs.csv: Main output file with all successfully scraped job listings
    - no_jobs_found.csv: Companies for which no jobs were found
    - error_records.csv: Companies that encountered errors during scraping

Author: Enhanced by AI Assistant
Version: 2.0.0
License: MIT
Last Updated: August 2025
"""

from jobspy import scrape_jobs
import requests
import os
import pandas as pd
import time
from requests.exceptions import RequestException
from typing import Optional, Union, List
import logging
import argparse
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variable for error logging compatibility
output_dir_global = ""


def validate_job_type(job_type: Optional[str]) -> bool:
    """
    Validate job type parameter against allowed values.

    Args:
        job_type: Job type string to validate

    Returns:
        bool: True if valid or None, False if invalid
    """
    if job_type is None:
        return True
    valid_types = ['fulltime', 'parttime', 'internship', 'contract']
    return job_type.lower() in valid_types


def format_duration(hours: int) -> str:
    """
    Format hours into human-readable duration string.

    Args:
        hours: Number of hours

    Returns:
        str: Formatted duration (e.g., "7 days", "2 weeks", "1 month")
    """
    if hours < 24:
        return f"{hours} hours"
    elif hours < 168:  # Less than a week
        days = hours // 24
        return f"{days} day{'s' if days != 1 else ''}"
    elif hours < 720:  # Less than a month
        weeks = hours // 168
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    else:
        months = hours // 720
        return f"{months} month{'s' if months != 1 else ''}"
def get_company_linkedin_id(company_name: str) -> Optional[str]:
    """
    Get LinkedIn company ID with comprehensive error handling and rate limiting.

    This function retrieves the LinkedIn company ID for a given company name by
    querying LinkedIn's typeahead API. It includes robust error handling for
    network issues, JSON parsing errors, and API response problems.

    Args:
        company_name (str): The name of the company to search for on LinkedIn.
            Should be the exact or close match to the company's LinkedIn page name.

    Returns:
        Optional[str]: LinkedIn company ID as a string if found, None if not found
        or if any error occurs. The ID can be used with linkedin_company_ids parameter
        in the scrape_jobs function.

    Error Handling:
        - Network errors (timeouts, connection issues): Logged and returns None
        - JSON decode errors: Logged to error_records.csv and returns None
        - Empty API responses: Logged as warning and returns None
        - Unexpected errors: Logged to error_records.csv and returns None

    Rate Limiting:
        - Uses a 10-second timeout for requests
        - No built-in rate limiting (handled by caller)

    Notes:
        - Uses LinkedIn's guest API endpoint (no authentication required)
        - API responses may be empty for companies not on LinkedIn
        - Function is case-insensitive but exact matches work best
        - Some company name variations may not return results

    Example:
        >>> company_id = get_company_linkedin_id("Google")
        >>> if company_id:
        ...     print(f"LinkedIn ID for Google: {company_id}")
        ... else:
        ...     print("Company not found on LinkedIn")
    """
    try:
        # URL encode company name to handle special characters and quotes
        encoded_company_name = quote_plus(company_name)
        url = f'https://www.linkedin.com/jobs-guest/api/typeaheadHits?typeaheadType=COMPANY&query={encoded_company_name}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes

        data = response.json()

        if not data or len(data) == 0:
            logger.warning(f"No company found for: {company_name}")
            return None

        company_id = data[0]['id']
        logger.debug(f"Found LinkedIn ID {company_id} for company: {company_name}")
        return company_id

    except requests.exceptions.JSONDecodeError:
        logger.error(f"Failed to decode JSON for company: {company_name}")
        if output_dir_global:
            save_error_records(company_name, "JSONDecodeError: Failed to decode JSON", output_dir_global)
        return None
    except RequestException as e:
        logger.error(f"Request failed for company {company_name}: {str(e)}")
        if output_dir_global:
            save_error_records(company_name, f"RequestException: {str(e)}", output_dir_global)
        return None
    except Exception as e:
        logger.error(f"Unexpected error for company {company_name}: {str(e)}")
        if output_dir_global:
            save_error_records(company_name, f"UnexpectedError: {str(e)}", output_dir_global)
        return None

def scrape_company_linkedin_jobs(
    company_name: str,
    location: str,
    fallback_company_name: Optional[str] = None,
    hours_old: int = 720,
    search_term: Optional[str] = None,
    linkedin_fetch_description: bool = False,
    results_wanted: Optional[int] = None,
    job_type: Optional[str] = None,
    distance: int = 50
) -> pd.DataFrame:
    """
    Scrape LinkedIn jobs for a specific company with advanced filtering options.

    This function attempts to retrieve LinkedIn jobs for a given company using the
    python-jobspy library. It includes comprehensive error handling and supports
    fallback company names for better job discovery.

    Args:
        company_name (str): Primary company name to search for jobs
        location (str): Geographic location for job search (e.g., "San Francisco, CA")
        fallback_company_name (str, optional): Alternative company name to try if
            primary search returns no results. Defaults to None.
        hours_old (int, optional): Filter jobs by hours since posting. Defaults to 720 (30 days).
            Note: This parameter filters jobs posted within the specified number of hours.
        search_term (str, optional): Additional search term to filter jobs (e.g., "Python developer").
            Defaults to None. When None, searches all jobs for the company.
        linkedin_fetch_description (bool, optional): Whether to fetch full job descriptions.
            Defaults to False. Setting to True increases request time significantly but provides
            more detailed job information including direct job URLs.
        results_wanted (int, optional): Maximum number of job results to retrieve.
            Defaults to None (retrieves all available jobs).
        job_type (str, optional): Type of employment to filter by.
            Valid options: 'fulltime', 'parttime', 'internship', 'contract'.
            Defaults to None (includes all job types).
        distance (int, optional): Search radius in miles from the specified location.
            Defaults to 50 miles.

    Returns:
        pd.DataFrame: DataFrame containing job listings with columns including:
            - site: Job board source (always 'linkedin' for this function)
            - title: Job title
            - company: Company name
            - location: Job location
            - date_posted: When the job was posted
            - job_type: Employment type (fulltime, parttime, etc.)
            - job_url: URL to the job posting
            - description: Job description (if linkedin_fetch_description=True)
            - salary information: min_amount, max_amount, currency, interval
            - Additional metadata: job_level, company_industry, etc.

            Returns empty DataFrame if no jobs found or if errors occur.

    Raises:
        Exception: Logs errors but does not raise them, returning empty DataFrame instead

    Notes:
        - LinkedIn API has rate limiting; function includes basic error handling
        - Large companies may have many job postings; consider using results_wanted to limit
        - Setting linkedin_fetch_description=True significantly increases execution time
        - Function automatically retries with fallback_company_name if provided and initial search fails

    Example:
        >>> jobs = scrape_company_linkedin_jobs(
        ...     company_name="Google",
        ...     location="Mountain View, CA",
        ...     hours_old=168,  # Last week
        ...     search_term="software engineer",
        ...     job_type="fulltime",
        ...     results_wanted=50
        ... )
        >>> print(f"Found {len(jobs)} jobs")
    """
    try:
        # Attempt to scrape jobs with the provided company name
        company_id = get_company_linkedin_id(company_name)
        if company_id is None:
            logger.warning(f"No LinkedIn ID found for company: {company_name}")
            return pd.DataFrame()

        company_id = int(company_id)

        # Build scrape_jobs parameters
        scrape_params = {
            "site_name": "linkedin",
            "linkedin_company_ids": [company_id],
            "location": location,
            "hours_old": hours_old,
            "distance": distance,
            "linkedin_fetch_description": linkedin_fetch_description
        }

        # Add optional parameters only if they are provided
        if search_term is not None:
            scrape_params["search_term"] = search_term
        if results_wanted is not None:
            scrape_params["results_wanted"] = results_wanted
        if job_type is not None:
            scrape_params["job_type"] = job_type

        jobs = scrape_jobs(**scrape_params)

        # If jobs are empty and fallback is available, try with fallback company name
        if jobs.empty and fallback_company_name:
            logger.info(f"No jobs found for {company_name}. Retrying with fallback: {fallback_company_name}")
            fallback_company_id = get_company_linkedin_id(fallback_company_name)
            if fallback_company_id is None:
                logger.warning(f"No LinkedIn ID found for fallback company: {fallback_company_name}")
                return pd.DataFrame()

            fallback_company_id = int(fallback_company_id)
            scrape_params["linkedin_company_ids"] = [fallback_company_id]
            jobs = scrape_jobs(**scrape_params)

        print(jobs)
        return jobs

    except Exception as e:
        logger.error(f"Error scraping jobs for {company_name}: {str(e)}")
        return pd.DataFrame()

def save_empty_or_none_records(company_name: str, output_dir: str):
    """Save records for companies with no jobs found."""
    try:
        output_file = os.path.join(output_dir, "no_jobs_found.csv")
        df = pd.DataFrame({"Company": [company_name]})
        if not os.path.exists(output_file):
            df.to_csv(output_file, index=False)
        else:
            df.to_csv(output_file, mode='a', header=False, index=False)
    except Exception as e:
        logger.error(f"Error saving no-jobs-found record for {company_name}: {str(e)}")


def save_error_records(company_name: str, error_message: str, output_dir: str):
    """Save records for companies where an error occurred."""
    try:
        output_file = os.path.join(output_dir, "error_records.csv")
        df = pd.DataFrame({"Company": [company_name], "Error": [error_message]})
        if not os.path.exists(output_file):
            df.to_csv(output_file, index=False)
        else:
            df.to_csv(output_file, mode='a', header=False, index=False)
    except Exception as e:
        logger.error(f"Error saving error record for {company_name}: {str(e)}")


def run_through_csv(
    csv_file: str,
    location: str,
    output_dir: str,
    start_idx: int = 0,
    end_idx: Optional[int] = None,
    hours_old: int = 720,
    search_term: Optional[str] = None,
    linkedin_fetch_description: bool = False,
    results_wanted: Optional[int] = None,
    job_type: Optional[str] = None,
    distance: int = 50
) -> None:
    """
    Process a CSV file containing company names and scrape LinkedIn jobs for each company.

    This function reads a CSV file with company information and systematically scrapes
    LinkedIn jobs for each company within the specified range. It includes comprehensive
    error handling, progress tracking, and outputs results to structured CSV files.

    Args:
        csv_file (str): Absolute path to the input CSV file containing company names.
            Must contain a 'Company' column. Optional 'Company Name for Emails' column
            will be used as fallback if provided.
        location (str): Geographic location for job search (e.g., "San Francisco, CA", "Remote").
        output_dir (str): Directory path where output files will be saved. Created if doesn't exist.
        start_idx (int, optional): Starting row index (0-based, inclusive). Defaults to 0.
        end_idx (int, optional): Ending row index (0-based, inclusive). If None, processes
            until the end of the file. Defaults to None.
        hours_old (int, optional): Filter jobs by hours since posting. Defaults to 720 (30 days).
        search_term (str, optional): Additional search term to filter jobs. Defaults to None.
        linkedin_fetch_description (bool, optional): Whether to fetch full job descriptions.
            Defaults to False. Warning: Setting to True significantly increases execution time.
        results_wanted (int, optional): Maximum number of jobs per company. Defaults to None.
        job_type (str, optional): Employment type filter. Options: 'fulltime', 'parttime',
            'internship', 'contract'. Defaults to None (all types).
        distance (int, optional): Search radius in miles. Defaults to 50.

    Output Files:
        Creates the following files in output_dir:
        - jobs.csv: Main output file containing all successfully scraped job listings
        - no_jobs_found.csv: Companies for which no jobs were found
        - error_records.csv: Companies that encountered errors during scraping

    CSV File Format:
        Input CSV must contain:
        - 'Company' (required): Primary company name for job search
        - 'Company Name for Emails' (optional): Alternative company name used as fallback

    Error Handling:
        - Invalid file paths or missing CSV files are logged and function returns early
        - Individual company errors are logged and saved to error_records.csv
        - Network errors, API errors, and parsing errors are handled gracefully
        - Processing continues even if individual companies fail

    Progress Tracking:
        - Logs progress for each company processed
        - Includes 1-second delay between companies to respect rate limits
        - Displays current company index and total companies

    Rate Limiting:
        - Built-in 1-second delay between company requests
        - Respects LinkedIn API limitations automatically through jobspy library
        - Logs warnings for rate limit encounters

    Example:
        >>> run_through_csv(
        ...     csv_file="/path/to/companies.csv",
        ...     location="New York, NY",
        ...     output_dir="/path/to/output",
        ...     start_idx=0,
        ...     end_idx=99,  # Process first 100 companies
        ...     hours_old=168,  # Last week only
        ...     job_type="fulltime",
        ...     results_wanted=25  # Max 25 jobs per company
        ... )

    Notes:
        - Large CSV files should be processed in batches using start_idx and end_idx
        - Monitor output files during execution to track progress
        - Consider using linkedin_fetch_description=True only for small batches
        - Function is resumable: can restart from any index if interrupted
    """
    try:
        global output_dir_global
        output_dir_global = output_dir

        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            return

        # Read CSV with explicit quote handling for proper parsing of quoted company names
        try:
            df = pd.read_csv(
                csv_file,
                quotechar='"',          # Handle double quotes properly
                skipinitialspace=True,   # Skip whitespace after delimiter
                na_filter=False,         # Don't convert strings to NaN
                dtype=str,              # Keep all data as strings
                encoding='utf-8'        # Handle special characters
            )
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding if utf-8 fails
            logger.warning(f"UTF-8 decoding failed for {csv_file}, trying latin-1 encoding")
            df = pd.read_csv(
                csv_file,
                quotechar='"',
                skipinitialspace=True,
                na_filter=False,
                dtype=str,
                encoding='latin-1'
            )

        if 'Company' not in df.columns:
            logger.error("CSV file must contain a 'Company' column")
            return

        total_rows = len(df)
        if end_idx is None or end_idx >= total_rows:
            end_idx = total_rows - 1

        if start_idx < 0 or start_idx > end_idx:
            logger.error(f"Invalid row range: {start_idx}-{end_idx}. Total rows in file: {total_rows}.")
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = os.path.join(output_dir, "jobs.csv")

        # Create output file with headers if it doesn't exist
        if not os.path.exists(output_file):
            pd.DataFrame().to_csv(output_file, index=False)

        logger.info(f"Starting batch processing: rows {start_idx} to {end_idx} ({end_idx - start_idx + 1} companies)")
        logger.info(f"Search parameters: location={location}, hours_old={hours_old}, job_type={job_type}")

        for idx in range(start_idx, end_idx + 1):
            company = df['Company'].iloc[idx]
            company_fallback = df['Company Name for Emails'].iloc[idx] if 'Company Name for Emails' in df.columns else None

            # Clean up company name: strip whitespace, handle empty values
            if pd.isna(company) or company == '' or str(company).strip() == '':
                logger.warning(f"Skipping empty company name at row {idx + 1}")
                continue

            # Clean and normalize company name
            company = str(company).strip()
            if company_fallback and not pd.isna(company_fallback):
                company_fallback = str(company_fallback).strip()
            else:
                company_fallback = None

            logger.info(f"Processing company {idx + 1}/{end_idx + 1}: {company}")

            try:
                jobs = scrape_company_linkedin_jobs(
                    company_name=company,
                    location=location,
                    fallback_company_name=company_fallback,
                    hours_old=hours_old,
                    search_term=search_term,
                    linkedin_fetch_description=linkedin_fetch_description,
                    results_wanted=results_wanted,
                    job_type=job_type,
                    distance=distance
                )

                if jobs.empty:
                    save_empty_or_none_records(company, output_dir)
                    logger.info(f"No jobs found for {company}")
                else:
                    # Append without writing index and only write header if file is empty
                    jobs.to_csv(output_file, mode='a', header=False, index=False)
                    logger.info(f"Saved {len(jobs)} jobs for {company}")

            except Exception as e:
                error_message = str(e)
                logger.error(f"Error processing company {company}: {error_message}")
                save_error_records(company, error_message, output_dir)

            print("\n")
            time.sleep(1)  # Rate limiting

        logger.info(f"Batch processing completed: {end_idx - start_idx + 1} companies processed")

    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")



def parse_arguments():
    """
    Parse command-line arguments for the LinkedIn Job Scraper.

    This function defines and parses all command-line arguments needed to run
    the LinkedIn job scraper with full parameterization support. It includes
    both required arguments and optional parameters with sensible defaults.

    Returns:
        argparse.Namespace: Parsed arguments object containing all parameters

    Required Arguments:
        csv_file: Path to input CSV file with company names
        location: Geographic location for job search
        output_dir: Directory for output files

    Optional Arguments:
        --start: Starting row index (default: 0)
        --end: Ending row index (default: process all)
        --hours-old: Filter by hours since posting (default: 720)
        --search-term: Additional search keywords (default: None)
        --fetch-description: Fetch full job descriptions (default: False)
        --results-wanted: Max results per company (default: None)
        --job-type: Employment type filter (default: None)
        --distance: Search radius in miles (default: 50)

    Example Usage:
        python index.py companies.csv "San Francisco, CA" ./output --hours-old 168 --job-type fulltime
    """
    parser = argparse.ArgumentParser(
        description='Enhanced LinkedIn Job Scraper with comprehensive filtering options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic usage:
    python %(prog)s companies.csv "San Francisco, CA" ./output

  Advanced filtering:
    python %(prog)s companies.csv "Remote" ./output \\
        --hours-old 168 \\
        --job-type fulltime \\
        --search-term "software engineer" \\
        --results-wanted 50 \\
        --distance 25

  Batch processing:
    python %(prog)s companies.csv "New York, NY" ./output \\
        --start 0 --end 99 \\
        --fetch-description \\
        --job-type internship

Job Types: fulltime, parttime, internship, contract
Output Files: jobs.csv, no_jobs_found.csv, error_records.csv
        """
    )

    # Required arguments
    parser.add_argument(
        'csv_file',
        help='Input CSV file containing company names (must have "Company" column)'
    )
    parser.add_argument(
        'location',
        help='Location to search for jobs (e.g., "San Francisco, CA", "Remote", "United States")'
    )
    parser.add_argument(
        'output_dir',
        help='Directory to save output files (created if it doesn\'t exist)'
    )

    # Optional batch processing arguments
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Starting row index (0-based, inclusive). Default: 0'
    )
    parser.add_argument(
        '--end',
        type=int,
        help='Ending row index (0-based, inclusive). Default: process all rows'
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
    parser.add_argument(
        '--results-wanted',
        type=int,
        help='Maximum number of job results per company (default: unlimited)'
    )
    parser.add_argument(
        '--distance',
        type=int,
        default=50,
        help='Search radius in miles from specified location. Default: 50'
    )

    # Optional performance arguments
    parser.add_argument(
        '--fetch-description',
        action='store_true',
        help='Fetch full job descriptions (WARNING: significantly increases execution time)'
    )

    return parser.parse_args()


if __name__ == "__main__":
    """
    Main execution block for the LinkedIn Job Scraper.

    This block parses command-line arguments and initiates the job scraping process
    with all specified parameters. It serves as the entry point for the application.

    The scraper will:
    1. Parse and validate all command-line arguments
    2. Set up output directories and logging
    3. Process the CSV file with specified company range
    4. Apply all filtering parameters to job searches
    5. Save results to structured output files

    For detailed usage information, run: python index.py --help
    """
    args = parse_arguments()

    # Validate arguments
    if not validate_job_type(args.job_type):
        logger.error(f"Invalid job type: {args.job_type}. Valid options: fulltime, parttime, internship, contract")
        exit(1)

    # Log the configuration being used
    logger.info("=" * 80)
    logger.info("LinkedIn Job Scraper - Enhanced Version")
    logger.info("=" * 80)
    logger.info(f"Input CSV: {args.csv_file}")
    logger.info(f"Location: {args.location}")
    logger.info(f"Output Directory: {args.output_dir}")
    logger.info(f"Row Range: {args.start} to {args.end if args.end else 'end'}")
    logger.info(f"Time Filter: {format_duration(args.hours_old)} ({args.hours_old} hours)")
    logger.info(f"Search Term: {args.search_term if args.search_term else 'None'}")
    logger.info(f"Job Type: {args.job_type if args.job_type else 'All types'}")
    logger.info(f"Results Wanted: {args.results_wanted if args.results_wanted else 'Unlimited'}")
    logger.info(f"Distance: {args.distance} miles")
    logger.info(f"Fetch Descriptions: {args.fetch_description}")
    if args.fetch_description:
        logger.warning("WARNING: --fetch-description enabled. This will significantly increase execution time!")
    logger.info("=" * 80)

    run_through_csv(
        csv_file=args.csv_file,
        location=args.location,
        output_dir=args.output_dir,
        start_idx=args.start,
        end_idx=args.end,
        hours_old=args.hours_old,
        search_term=args.search_term,
        linkedin_fetch_description=args.fetch_description,
        results_wanted=args.results_wanted,
        job_type=args.job_type,
        distance=args.distance
    )