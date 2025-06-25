# AI_DOC

This project contains a small set of tools for collecting and analysing
personal glucose readings.  The main application runs a local assistant
that communicates with an LLM through the `core` package.  Additional
scripts allow daily log entry, report viewing and automatic data
synchronisation.

To run the assistant interactively:

```bash
python core/main.py
```

Optional helper scripts are:

- `auto_sync.py` &ndash; periodically fetch data from the Nightscout API
- `daily_log.py` &ndash; enter meals and comments for a day
- `core/report_viewer.py` &ndash; show reports for specific periods

The code expects Python 3.10+ and the packages listed in
`requirements.txt`.
