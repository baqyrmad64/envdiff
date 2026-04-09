# envdiff

A lightweight CLI tool to compare `.env` files across environments and flag missing or mismatched keys.

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourusername/envdiff.git
cd envdiff
pip install -e .
```

## Usage

Compare two `.env` files:

```bash
envdiff .env.local .env.production
```

Compare multiple environment files:

```bash
envdiff .env.development .env.staging .env.production
```

**Example Output:**

```
Comparing 3 environment files...

✓ DATABASE_URL: present in all files
✗ API_KEY: missing in .env.production
✗ DEBUG_MODE: present in .env.development only
⚠ PORT: value mismatch across environments
  .env.development: 3000
  .env.staging: 8080
  .env.production: 8080

Summary: 1/4 keys consistent across all environments
```

## Options

- `--ignore-values`: Only check for key presence, ignore value differences
- `--json`: Output results in JSON format
- `--strict`: Exit with error code if any inconsistencies found

## License

MIT License - see [LICENSE](LICENSE) file for details.