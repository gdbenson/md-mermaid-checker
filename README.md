# md-mermaid-checker

A fast, reliable tool for validating Mermaid.js diagrams embedded in Markdown files.

## Features

- ✅ Validates all `mermaid` and `mermaidjs` code blocks in your Markdown files
- 🚀 Fast validation using the official Mermaid CLI (`mmdc`)
- 📁 Supports glob patterns for processing multiple files
- 🎨 Configurable themes and Mermaid settings
- 📊 Clear error reporting with line numbers
- 🔧 Works with or without global `mmdc` installation (uses `npx` as fallback)

## Prerequisites

- Node.js and npm (for running the Mermaid CLI)
- Python 3.8 or higher

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager written in Rust:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install md-mermaid-checker as a tool
uv tool install md-mermaid-checker

# Or install from GitHub directly
uv tool install git+https://github.com/gdbenson/md-mermaid-checker

# Or for development (editable install)
git clone https://github.com/gdbenson/md-mermaid-checker
cd md-mermaid-checker
uv tool install -e .
```

### Using pip

```bash
# From PyPI (once published)
pip install md-mermaid-checker

# From GitHub
pip install git+https://github.com/gdbenson/md-mermaid-checker

# For development
git clone https://github.com/gdbenson/md-mermaid-checker
cd md-mermaid-checker
pip install -e .
```

### Using pipx

For isolated installation:

```bash
pipx install md-mermaid-checker
```

## Usage

```bash
# Check a single file
md-mermaid-checker README.md

# Check multiple files
md-mermaid-checker README.md CONTRIBUTING.md

# Check all Markdown files in a directory tree
md-mermaid-checker "docs/**/*.md"

# Use a custom Mermaid config and theme
md-mermaid-checker -c mermaid.config.json -t dark "**/*.md"

# Keep temporary files for debugging
md-mermaid-checker -k README.md

# Quiet mode (only show errors)
md-mermaid-checker -q "docs/**/*.md"
```

## Command-line Options

- `inputs`: Markdown files or glob patterns to check
- `-c, --config`: Path to Mermaid configuration JSON file
- `-t, --theme`: Mermaid theme (base, default, dark, forest, neutral)
- `-k, --keep`: Keep temporary files for debugging
- `-q, --quiet`: Only print errors and summary

## Exit Codes

- `0`: All Mermaid blocks are valid (or no blocks found)
- `1`: At least one invalid Mermaid block was found
- `2`: Usage or environment error (e.g., `mmdc` not available)

## How It Works

1. Scans Markdown files for code blocks marked as `mermaid` or `mermaidjs`
2. Extracts each diagram into a temporary file
3. Validates using the Mermaid CLI (`mmdc`)
4. Reports results with file names and line numbers
5. Cleans up temporary files (unless `-k` is specified)

## Development

```bash
# Clone the repository
git clone https://github.com/gdbenson/md-mermaid-checker
cd md-mermaid-checker

# Install in development mode with uv
uv tool install -e .

# Or with pip
pip install -e .

# Run tests (if available)
python -m pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
