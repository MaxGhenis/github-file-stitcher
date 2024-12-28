# GitHub Stitcher 🧵

A Streamlit app that helps you stitch together content from various GitHub sources including repositories, pull requests, issues, and specific files.

## Features

- **Multiple Content Sources**

  - Individual files via blob URLs
  - Repository directories via tree URLs
  - Pull request diffs
  - Issue discussions and comments
  - Pattern-matched files across repositories

- **Branch Support**

  - Access content from any branch or tag
  - Full support for branch names containing slashes (e.g., feature/branch)
  - Defaults to repository's default branch if not specified

- **Advanced Filtering**

  - Filter files by path patterns
  - Filter content by line patterns
  - Include or exclude matching content
  - Support for regular expressions

- **Output Options**
  - Formatted markdown output
  - Downloadable content
  - Syntax highlighting

## Supported URL Formats

The app supports various GitHub URL formats:

```
# Individual files
github.com/owner/repo/blob/branch/path/to/file.py

# Directory contents
github.com/owner/repo/tree/branch/path/to/dir

# Pull requests
github.com/owner/repo/pull/123

# Issues
github.com/owner/repo/issues/456

# Repository root
github.com/owner/repo

# Pattern matching (regex)
regex:.*\.py$
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/github-stitcher.git
   cd github-stitcher
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.streamlit/secrets.toml` file with your GitHub token:

   ```toml
   GITHUB_TOKEN = "your-github-token"
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage Examples

### Fetching Specific Files

To fetch multiple Python files from a repository:

```
https://github.com/owner/repo/blob/main/src/module1.py
https://github.com/owner/repo/blob/main/src/module2.py
```

### Fetching Directory Contents

To fetch all files in a directory:

```
https://github.com/owner/repo/tree/main/src
```

### Fetching from Feature Branches

Support for complex branch names:

```
https://github.com/owner/repo/tree/feature/branch-name/src
https://github.com/owner/repo/blob/user/feature-123/file.py
```

### Pattern Matching

Find all Python files in a repository:

```
regex:.*\.py$
```

## Project Structure

```
github_stitcher/
├── app.py                # Main Streamlit application
├── core/                 # Core functionality
│   ├── github_api.py     # GitHub API interface
│   ├── parsers.py       # URL parsing utilities
│   └── processors/      # Content processors
│       ├── base.py      # Base processor class
│       ├── repo.py      # Repository content processor
│       ├── pr.py        # Pull request processor
│       └── issue.py     # Issue processor
├── ui/                  # User interface components
└── config.py           # Configuration settings
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[MIT License](LICENSE)
