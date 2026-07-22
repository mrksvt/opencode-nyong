---
name: postman
description: Use when running Postman collections, testing APIs, managing workspaces, or interacting with Postman resources from the command line. Also use when setting up Postman MCP server for AI agent integration.
---

# Postman CLI & MCP Server

Your knowledge of Postman CLI flags and commands may be outdated. **Prefer retrieval over pre-training** for any Postman task.

## Retrieval Sources

Fetch the **latest** information before writing or reviewing Postman commands. Do not rely on baked-in knowledge for CLI flags or config fields.

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Postman CLI help | `postman --help` or `postman <command> --help` | CLI commands, flags, options |
| Postman MCP docs | `https://learning.postman.com/docs/reference/postman-api/postman-mcp-server/overview` | MCP server setup, configurations |
| Postman MCP GitHub | `https://github.com/postmanlabs/postman-mcp-server` | Source code, examples, updates |

## FIRST: Check if Postman CLI is installed and authenticated

Check if Postman CLI is installed by running:

```bash
postman --version  # Requires v1.x+
```

If Postman CLI is not installed, install it via npm:

```bash
npm install -g @postman/cli
```

Check authentication status:

```bash
postman login --help  # Shows login options
```

If not authenticated, sign in:

```bash
# Standard login (opens browser)
postman login

# Login with API key
postman login --with-api-key <api-key>

# Login to EU region
postman login --region eu
```

## Quick Reference: Core Commands

| Task | Command |
|------|---------|
| Run collection by ID | `postman collection run <collection-id>` |
| Run collection with environment | `postman collection run <collection-id> -e <environment-id>` |
| Run local collection file | `postman collection run ./collection.json` |
| Send HTTP request | `postman request <method> <url>` |
| Search collections | `postman search collections "query"` |
| Search requests | `postman search requests "query"` |
| Run monitor | `postman monitor run <monitor-id>` |
| Lint API | `postman api lint <api-id>` |
| Push workspace changes | `postman workspace push` |

---

## Collection Commands

### Run Collection

```bash
# Run by collection ID
postman collection run 123456-45159473-1e45-1f34-5678-1234567890ab

# Run with environment
postman collection run <collection-id> -e <environment-id>

# Run local collection file
postman collection run ./my-collection.json

# Run with specific requests only
postman collection run <collection-id> -i "FolderName/RequestName"

# Run with iteration data (CSV/JSON)
postman collection run <collection-id> -d ./test-data.csv -n 5

# Run with reporters
postman collection run <collection-id> -r cli,json,html

# Run with bail on first failure
postman collection run <collection-id> --bail

# Run with custom timeout
postman collection run <collection-id> --timeout 60000

# Run with delay between requests
postman collection run <collection-id> --delay-request 1000

# Run and export report
postman collection run <collection-id> -r json --reporter-json-export ./report.json
```

### Lint Collection

```bash
# Lint local collection file
postman collection lint ./my-collection.json

# Lint directory of collections
postman collection lint ./collections/
```

### Migrate Collection

```bash
# Migrate v2.1 to v3 format
postman collection migrate ./old-collection.json
```

---

## Request Commands

### Basic Requests

```bash
# Simple GET request
postman request https://api.example.com/users

# GET with explicit method
postman request GET https://api.example.com/users

# POST with JSON body
postman request POST https://api.example.com/users \
  --body '{"name": "Alice", "email": "alice@example.com"}'

# PUT with body from file
postman request PUT https://api.example.com/users/123 --body @user-data.json

# DELETE request
postman request DELETE https://api.example.com/users/123
```

### Authentication

```bash
# Bearer token
postman request https://api.example.com/protected \
  --auth-bearer-token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Basic auth
postman request https://api.example.com/protected \
  --auth-basic-username myuser \
  --auth-basic-password mypass

# API Key in header
postman request https://api.example.com/data \
  --auth-apikey-key "X-API-Key" \
  --auth-apikey-value "abc123xyz" \
  --auth-apikey-in header

# API Key in query parameter
postman request https://api.example.com/data \
  --auth-apikey-key "apikey" \
  --auth-apikey-value "abc123xyz" \
  --auth-apikey-in query
```

### Headers and Forms

```bash
# Custom headers
postman request https://api.example.com/data \
  -H "Content-Type:application/json" \
  -H "X-Custom-Header:custom-value"

# Multipart form data (file upload)
postman request POST https://api.example.com/upload \
  -f "file=@document.pdf" \
  -f "title=My Document"
```

### Environment Variables

```bash
# Use Postman environment file
postman request https://api.example.com/{{endpoint}} \
  -e production.postman_environment.json \
  -H "Authorization:Bearer {{auth_token}}"
```

### Scripts

```bash
# Inline pre-request script
postman request https://api.example.com/data \
  --script-pre-request "pm.environment.set('timestamp', Date.now());"

# Inline post-request script
postman request https://api.example.com/users \
  --script-post-request "console.log(pm.response.json());"

# Load scripts from files
postman request https://api.example.com/data \
  --script-pre-request @setup.js \
  --script-post-request @validate.js
```

### Retry Logic

```bash
# Retry failed requests
postman request https://api.flaky-service.com/data \
  --retry 3 \
  --retry-delay 2000
```

### Output Control

```bash
# Save response to JSON file
postman request https://api.example.com/data --output response.json

# Response only (for piping)
postman request https://api.example.com/data --response-only | jq '.results[]'

# Verbose mode
postman request https://api.example.com/data --verbose

# Debug mode
postman request https://api.example.com/data --debug
```

---

## Search Commands

```bash
# Search collections
postman search collections "auth"

# Search requests
postman search requests "login"

# Search workspaces
postman search workspaces "backend"

# Search with filters
postman search requests "auth" --filter "method=POST AND visibility=public"

# Search with JSON output
postman search collections "api" --output json

# Limit results
postman search requests "user" --limit 5
```

---

## Workspace Commands

```bash
# Prepare local collections for push
postman workspace prepare

# Push changes to Postman workspace
postman workspace push
```

---

## Monitor Commands

```bash
# Run monitor
postman monitor run <monitor-id>
```

---

## API Commands

```bash
# Lint API schema
postman api lint <api-id>

# Publish API version
postman api publish <api-id>
```

---

## Context Commands (Beta)

```bash
# Get agent instructions
postman context instructions

# Get discovery instructions
postman context instructions discovery

# Get code generation instructions
postman context instructions code-generation

# Get maintenance instructions
postman context instructions maintenance
```

---

## Postman MCP Server

The Postman MCP server enables AI agents to interact with Postman resources via Model Context Protocol.

### Remote Server (Recommended)

Add to your `opencode.jsonc`:

```jsonc
{
  "mcp": {
    "postman": {
      "type": "remote",
      "url": "https://mcp.postman.com/minimal",
      "enabled": true
    }
  }
}
```

**Server modes:**
- `/minimal` — Essential tools for basic operations (default)
- `/code` — Tools for generating client code from API definitions
- `/mcp` — All available tools (100+)

**EU region:**
```jsonc
{
  "mcp": {
    "postman": {
      "type": "remote",
      "url": "https://mcp.eu.postman.com/minimal",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:POSTMAN_API_KEY}"
      }
    }
  }
}
```

### Local Server

Add to your `opencode.jsonc`:

```jsonc
{
  "mcp": {
    "postman": {
      "type": "local",
      "command": ["npx", "-y", "@postman/postman-mcp-server"],
      "enabled": true,
      "environment": {
        "POSTMAN_API_KEY": "{env:POSTMAN_API_KEY}"
      }
    }
  }
}
```

**With mode flag:**
```jsonc
{
  "mcp": {
    "postman": {
      "type": "local",
      "command": ["npx", "-y", "@postman/postman-mcp-server", "--code"],
      "enabled": true,
      "environment": {
        "POSTMAN_API_KEY": "{env:POSTMAN_API_KEY}"
      }
    }
  }
}
```

### Authentication

**OAuth (Remote only):**
- No configuration needed
- OpenCode will prompt for authentication when first used
- Or manually trigger: `opencode mcp auth postman`

**API Key:**
1. Generate API key at https://www.postman.com/settings/api-keys
2. Set environment variable: `export POSTMAN_API_KEY=your-key-here`
3. Configure in `opencode.jsonc` as shown above

### Using Postman MCP Tools

Once configured, use Postman tools in your prompts:

```
List my Postman workspaces. use postman
Show me the collections in my workspace. use postman
Run the health check collection. use postman
```

---

## Common Patterns

### CI/CD Integration

```bash
# Run collection in CI with JUnit report
postman collection run <collection-id> \
  -r junit \
  --reporter-junit-export ./test-results.xml \
  --bail \
  --timeout 300000

# Health check with validation
postman request https://api.production.com/health \
  --timeout 5000 \
  --retry 3 \
  --retry-delay 1000 \
  --script-post-request "pm.test('Health check', function() { \
    const resp = pm.response.json(); \
    pm.expect(resp.status).to.equal('healthy'); \
  });"
```

### Chain Requests

```bash
# Get token and use it
TOKEN=$(postman request POST https://api.example.com/login \
  --body '{"username":"admin","password":"pass"}' \
  --response-only | jq -r '.token')

postman request https://api.example.com/protected \
  --auth-bearer-token "${TOKEN}"
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Not authenticated | Run `postman login` first |
| Wrong region | Use `--region eu` for EU |
| Missing environment | Pass `-e <env-id>` or use `--env-var` |
| Collection not found | Check ID or use local file path |
| Timeout errors | Increase `--timeout` value |
| SSL errors | Use `--insecure` flag (dev only) |

## Exit Codes

- `0`: Success (2xx-3xx response, all tests passed)
- `N`: Number of failed tests (e.g., exit code 3 = 3 tests failed)
