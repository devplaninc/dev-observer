## Setup

Create file [.env.local](.env.local) and add following there:
```
DEV_OBSERVER__GITHUB__PERSONAL_TOKEN=<Github personal token, use `gh auth token` to get>
GOOGLE_API_KEY=<GOOGLE_API_TOKEN to use for google-genai>
```

## Testing

```bash
uv run scripts/self_analysis/main.py
```