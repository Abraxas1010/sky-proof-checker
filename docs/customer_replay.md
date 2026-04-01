# Customer Replay

`sky-proof-checker` is the independent replay surface for the SKY stack. A
delivery package from `verified-sky-checker` should include:

- `bundle.sky.json`
- `manifest.json`
- a replay command: `python3 python/sky_checker.py bundle.sky.json`

Local replay against a packaged bundle:

```bash
python3 python/sky_checker.py /path/to/bundle.sky.json
```

The checker is intentionally small and does not require Lean, a compiler, or
the service repo. That is the point of the customer replay lane.
