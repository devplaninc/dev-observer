## Setup

Create file [.env.local](.env.local) and add following there:
```
GITHUB_PERSONAL_TOKEN=<Github personal token, use `gh auth token` to get>
```

## Testing

```bash
uv run scripts/analysis/process.py --repo git@github.com:devplaninc/webapp.git
```