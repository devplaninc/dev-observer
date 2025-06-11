## Setup

Create file [.env.local.secrets](.env.local.secrets) and add following there:
```
DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN=<Github personal token, use `gh auth token` to get>
DEV_OBSERVER__GIT__GITHUB__PRIVATE_KEY=<GH private key if app auth is used>
DEV_OBSERVER__GIT__GITHUB__APP_ID="<GH APP ID if app auth is used>"
GOOGLE_API_KEY=<GOOGLE_API_TOKEN to use for google-genai>
DEV_OBSERVER__USERS_MANAGEMENT__CLERK__SECRET_KEY=<get key from Clerk>
```

## Testing

```bash
uv run scripts/self_analysis/main.py
```