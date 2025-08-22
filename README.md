# Enhanced LinkedIn Job Scraper

A comprehensive LinkedIn job scraping tool with advanced filtering options, robust error handling, and batch processing capabilities.

## Features

### Core Functionality
- **Multi-company batch processing** from CSV files
- **Advanced job filtering** by time, type, location, and keywords
- **Comprehensive error handling** with detailed logging
- **Progress tracking** and structured output files
- **Fallback company name support** for better job discovery
- **Command-line interface** with extensive parameter support

### New Parameters Added
- `hours_old`: Filter jobs by hours since posting (default: 720 hours / 30 days)
- `search_term`: Additional keywords to filter jobs (optional)
- `linkedin_fetch_description`: Fetch full job descriptions (default: False)
- `results_wanted`: Maximum number of jobs per company (optional)
- `job_type`: Employment type filter (fulltime, parttime, internship, contract)
- `distance`: Search radius in miles (default: 50)

## Installation

```bash
pip install python-jobspy pandas requests
```

## Usage

### Basic Usage
```bash
python index.py companies.csv "San Francisco, CA" ./output
```

### Advanced Filtering
```bash
python index.py companies.csv "Remote" ./output \
    --hours-old 168 \
    --job-type fulltime \
    --search-term "software engineer" \
    --results-wanted 50 \
    --distance 25
```

### Batch Processing
```bash
python index.py companies.csv "New York, NY" ./output \
    --start 0 --end 99 \
    --fetch-description \
    --job-type internship
```

## Command Line Arguments

### Required Arguments
- `csv_file`: Input CSV file with company names (must have "Company" column)
- `location`: Geographic location for job search
- `output_dir`: Directory for output files

### Optional Arguments
- `--start INT`: Starting row index (0-based, default: 0)
- `--end INT`: Ending row index (0-based, default: process all)
- `--hours-old INT`: Filter by hours since posting (default: 720)
- `--search-term STR`: Additional search keywords
- `--job-type {fulltime,parttime,internship,contract}`: Employment type filter
- `--results-wanted INT`: Max results per company
- `--distance INT`: Search radius in miles (default: 50)
- `--fetch-description`: Fetch full job descriptions (WARNING: slow)

## Input CSV Format

### Required Columns
- `Company`: Primary company name for job search

### Optional Columns
- `Company Name for Emails`: Alternative company name used as fallback

### Example CSV
```csv
Company,Company Name for Emails
Google,Google LLC
Microsoft,Microsoft Corporation
Apple Inc,Apple
Meta,Facebook
```

## Output Files

The scraper creates three output files in the specified directory:

### 1. jobs.csv
Main output file containing all successfully scraped job listings with columns:
- `site`: Job board source (always 'linkedin')
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `date_posted`: When the job was posted
- `job_type`: Employment type
- `job_url`: URL to the job posting
- `description`: Job description (if --fetch-description enabled)
- `salary_source`: Salary information source
- `min_amount`, `max_amount`: Salary range
- `currency`: Salary currency
- `interval`: Salary interval (yearly, hourly, etc.)
- Additional metadata columns

### 2. no_jobs_found.csv
Companies for which no jobs were found:
- `Company`: Company name

### 3. error_records.csv
Companies that encountered errors during scraping:
- `Company`: Company name
- `Error`: Error description

## Performance Considerations

### Rate Limiting
- Built-in 1-second delay between company requests
- Respects LinkedIn API limitations automatically
- Monitor logs for rate limit warnings

### Execution Time
- **Normal mode**: ~1-2 seconds per company
- **With --fetch-description**: ~5-10 seconds per company
- **Large batches**: Consider processing in smaller chunks

### Memory Usage
- Efficient memory usage with streaming CSV processing
- Output files written incrementally
- Safe for processing thousands of companies

## Error Handling

### Network Errors
- Automatic retry logic for transient failures
- Detailed error logging with timestamps
- Graceful degradation for API issues

### Data Validation
- Input CSV validation
- Parameter validation with helpful error messages
- Fallback mechanisms for missing data

### Recovery
- Process continues even if individual companies fail
- Resumable processing using --start and --end parameters
- Detailed error records for troubleshooting

## Advanced Usage Examples

### Process specific time ranges
```bash
# Jobs from last 24 hours only
python index.py companies.csv "Remote" ./output --hours-old 24

# Jobs from last week
python index.py companies.csv "San Francisco, CA" ./output --hours-old 168
```

### Target specific job types
```bash
# Full-time positions only
python index.py companies.csv "New York, NY" ./output --job-type fulltime

# Internships only
python index.py companies.csv "Boston, MA" ./output --job-type internship
```

### Combine multiple filters
```bash
# Python jobs, full-time, from last 3 days, max 25 per company
python index.py companies.csv "Remote" ./output \
    --search-term "python developer" \
    --job-type fulltime \
    --hours-old 72 \
    --results-wanted 25
```

### Resume interrupted processing
```bash
# Process companies 100-199 (if previous run stopped at company 99)
python index.py companies.csv "Seattle, WA" ./output --start 100 --end 199
```

## Monitoring and Logging

### Log Levels
- **INFO**: Normal progress updates
- **WARNING**: Non-critical issues (e.g., no jobs found)
- **ERROR**: Critical failures requiring attention

### Progress Tracking
```
2025-08-22 10:30:15 - INFO - Processing company 25/100: Google
2025-08-22 10:30:17 - INFO - Saved 15 jobs for Google
2025-08-22 10:30:19 - INFO - Processing company 26/100: Microsoft
```

### Configuration Summary
The scraper logs all configuration details at startup:
```
================================================================================
LinkedIn Job Scraper - Enhanced Version
================================================================================
Input CSV: companies.csv
Location: San Francisco, CA
Output Directory: ./output
Row Range: 0 to end
Time Filter: 1 week (168 hours)
Search Term: software engineer
Job Type: fulltime
Results Wanted: 50
Distance: 25 miles
Fetch Descriptions: False
================================================================================
```

## Troubleshooting

### Common Issues

1. **No jobs found for any company**
   - Check if company names match LinkedIn exactly
   - Verify location spelling
   - Try broader search terms

2. **Rate limiting errors**
   - Reduce batch size
   - Increase delays between requests
   - Use proxies if available

3. **Empty output files**
   - Check CSV file format
   - Verify column names
   - Review error_records.csv for issues

4. **Slow performance**
   - Avoid --fetch-description for large batches
   - Process in smaller chunks
   - Use specific job type filters

### Getting Help
- Check error_records.csv for specific error messages
- Review log output for warnings
- Validate input CSV format
- Test with a small batch first

## License

MIT License - feel free to modify and distribute.

## Contributing

Contributions welcome! Please:
1. Test changes thoroughly
2. Update documentation
3. Follow existing code style
4. Add appropriate logging
