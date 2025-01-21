# LinkedIn Jobs Scraper by Company Name

This scraper will get the linkedin jobs of 30 days before of companies specified in a CSV. Essentially what [JobSpy](https://github.com/Bunsly/JobSpy) is missing because you have to search there by linkedin company ID for it to return accurate results. Yielding almost if not 100% accuracy, this uses the [hidden official LinkedIn API](https://gist.github.com/Diegiwg/51c22fa7ec9d92ed9b5d1f537b9e1107) for autocompleting company names used when tagging them in a post.

## Requirements

```py
pip install python-jobspy argparse
```

## Notes

1. Columns required (Company, Company Name from Email) as exported from Apollo
2. Uses Company column first then fallbacks to CNFE
3. Saves the returned rows in the following files each company name:
 - jobs.csv
 - no_jobs_found.csv
 - error_records.csv
4. You can fork this repo to adjust the arguments based on your use case

## Arguments

- Format: `python index.py <1> <2> <3> --start <4> --end <5>`
- Sample: `python index.py sample.CSV "United States" ./path --start 0 --end 10000`

1. CSV file of names
2. Country or location
3. Path where CSVs will be saved
4. Start index of CSV (Optional)
5. End index of CSV (Optional)

## Error 429

If a company returned error 429 and saved in `error_records`, it was rate limited but you can try again with `python index.py error_records.CSV "United States" ./path`

## Technique

1. Use GitHub Codespace (you can have up to two active per account)
2. Split the scrape in two terminals each codespace. If you have 10,000 company names, split in `--start 0 --end 5000` and `--start 5000 --end 10000` or 2500 each terminal for each codespace. More than two terminals increases chances of rate limited by the autocomplete API.

## Room for improvement

- Request are I/O bound instead of CPU bound so more cores will have little effect. Experiment using async in python.
- Implement batch save every batch size of your choice