# LinkedIn Job Scraper with Smart Fallback System

A comprehensive LinkedIn job scraper built with the `python-jobspy` library, featuring intelligent company name matching, advanced parameterization, and robust CSV handling capabilities.

## Features

### 🎯 Smart Fallback System
- **Three-tier fallback mechanism** for maximum job discovery success:
  1. **Primary search**: Uses the original company name
  2. **Manual fallback**: Uses user-provided alternative company name
  3. **Auto-cleaned fallback**: Automatically removes corporate suffixes (Inc., LLC, Corp., etc.)

### 📊 Advanced Parameterization
- **Time filtering**: Filter jobs by hours since posting (default: 30 days)
- **Search terms**: Add specific job search keywords
- **Job types**: Filter by employment type (fulltime, parttime, internship, contract)
- **Location radius**: Customizable search distance in miles
- **Result limits**: Control maximum number of results returned
- **Description fetching**: Option to retrieve full job descriptions

### 📁 Robust CSV Handling
- **Quote-aware parsing**: Handles company names with commas and special characters
- **Encoding support**: Multiple encoding fallbacks (UTF-8, Latin-1, CP1252)
- **Data validation**: Skips empty or invalid company entries
- **Flexible column mapping**: Supports various CSV formats

### 🔄 Error Handling & Logging
- **Comprehensive logging**: Track all scraping attempts and fallbacks
- **Rate limiting awareness**: Built-in error handling for API limits
- **Graceful degradation**: Returns empty results instead of crashing

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install python-jobspy pandas requests argparse
   ```

## Usage

### Command Line Interface

#### Basic Usage
```bash
python index.py --csv companies.csv --location "San Francisco, CA"
```

#### Advanced Usage with Parameters
```bash
python index.py \
  --csv companies.csv \
  --location "New York, NY" \
  --hours_old 168 \
  --search_term "software engineer" \
  --job_type fulltime \
  --distance 25 \
  --results_wanted 100 \
  --fetch_descriptions
```

### Parameter Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--csv` | str | Required | Path to CSV file containing company names |
| `--location` | str | Required | Geographic location for job search |
| `--hours_old` | int | 720 | Filter jobs posted within X hours (720 = 30 days) |
| `--search_term` | str | None | Additional search keywords (e.g., "Python developer") |
| `--job_type` | str | None | Employment type: `fulltime`, `parttime`, `internship`, `contract` |
| `--distance` | int | 50 | Search radius in miles from location |
| `--results_wanted` | int | None | Maximum number of results per company |
| `--fetch_descriptions` | flag | False | Fetch full job descriptions (slower but more detailed) |

### CSV Format Requirements

Your CSV file should contain a `Company` column with company names:

```csv
Company,Company Name for Emails
"Apple Inc.","Apple"
"Microsoft Corporation","Microsoft"
"Google LLC","Alphabet Inc."
"Amazon.com, Inc.","Amazon"
```

**Supported formats:**
- Simple company names: `Apple`, `Microsoft`
- Companies with commas: `"Amazon.com, Inc."`, `"2Go Group, Inc."`
- Optional fallback column: `Company Name for Emails`

## Smart Fallback Examples

### Automatic Suffix Removal
The scraper automatically tries cleaned company names when the original search fails:

| Original Company Name | Auto-Cleaned Fallback |
|----------------------|------------------------|
| `Apple Inc.` | `Apple` |
| `Microsoft Corporation` | `Microsoft` |
| `Google LLC` | `Google` |
| `Amazon.com, Inc.` | `Amazon.com` |
| `Tesla, Inc.` | `Tesla` |

### Fallback Sequence
For each company, the scraper tries up to 3 variations:

1. **Original name**: `"Microsoft Corporation"`
2. **Manual fallback**: `"Microsoft"` (if provided in CSV)
3. **Auto-cleaned**: `"Microsoft"` (suffix removed automatically)

## Programmatic Usage

```python
from index import scrape_company_linkedin_jobs

# Basic usage
jobs = scrape_company_linkedin_jobs(
    company_name="Apple Inc.",
    location="Cupertino, CA"
)

# Advanced usage with all parameters
jobs = scrape_company_linkedin_jobs(
    company_name="Google LLC",
    location="Mountain View, CA",
    fallback_company_name="Alphabet Inc.",
    hours_old=168,  # Last week
    search_term="machine learning engineer",
    job_type="fulltime",
    distance=25,
    results_wanted=50,
    linkedin_fetch_description=True
)

print(f"Found {len(jobs)} jobs")
```

## Output Format

The scraper returns a pandas DataFrame with the following columns:

### Core Job Information
- `site`: Job board source (always 'linkedin')
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `date_posted`: When the job was posted
- `job_type`: Employment type
- `job_url`: Direct link to job posting

### Salary Information
- `min_amount`: Minimum salary
- `max_amount`: Maximum salary
- `currency`: Salary currency
- `interval`: Salary interval (yearly, monthly, etc.)

### Additional Metadata
- `description`: Full job description (if `fetch_descriptions=True`)
- `job_level`: Seniority level
- `company_industry`: Industry classification
- `benefits`: Listed benefits (if available)

## Logging

The scraper provides detailed logging for troubleshooting:

```
INFO - Processing company: Apple Inc.
INFO - No jobs found for Apple Inc. Retrying with cleaned name: Apple
INFO - Found 15 jobs using cleaned company name: Apple
INFO - Successfully scraped 15 jobs for Apple Inc.
```

## Error Handling

### Common Issues and Solutions

1. **No jobs found**: The scraper automatically tries fallback names
2. **Rate limiting**: Built-in delays and error handling
3. **CSV parsing errors**: Multiple encoding attempts and quote handling
4. **Invalid company names**: Automatic skipping with logging

### Best Practices

- **Use reasonable time filters**: Don't go back too far (hours_old)
- **Limit results for testing**: Use `results_wanted` parameter
- **Monitor rate limits**: LinkedIn has usage restrictions
- **Check logs**: Use logging output to debug issues

## Dependencies

- `python-jobspy`: Core job scraping functionality
- `pandas`: CSV handling and data manipulation
- `requests`: HTTP requests and URL encoding
- `argparse`: Command-line argument parsing
- `logging`: Comprehensive logging system

## Examples

### Test the Fallback System
```bash
python test_fallbacks.py
```

### Scrape Multiple Companies
```bash
python index.py --csv examples/companies.csv --location "Seattle, WA" --job_type fulltime
```

### Get Recent Jobs Only
```bash
python index.py --csv companies.csv --location "Austin, TX" --hours_old 24
```

### Search for Specific Roles
```bash
python index.py --csv companies.csv --location "Boston, MA" --search_term "data scientist"
```

## Contributing

This scraper is designed to be robust and extensible. Key areas for enhancement:

- Additional job sites support
- More sophisticated company name matching
- Enhanced data export formats
- Integration with job tracking systems

## Notes

- **LinkedIn Rate Limits**: Be respectful of LinkedIn's API usage policies
- **Legal Compliance**: Ensure your usage complies with LinkedIn's terms of service
- **Data Privacy**: Handle scraped data responsibly and in compliance with privacy laws

---

**Version**: 2.0 with Smart Fallback System
**Last Updated**: August 2025
