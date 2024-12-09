# GitHub Stitcher 🧵

A Streamlit app that helps you stitch together content from various GitHub sources including repositories, pull requests, and issues.

## Features

- **Multiple Content Sources**

  - Repository files and folders
  - Pull request diffs
  - Issue discussions and comments
  - Pattern-matched files across repositories

- **Advanced Filtering**

  - Filter files by path patterns
  - Filter content by line patterns
  - Include or exclude matching content
  - Support for regular expressions

- **Output Options**
  - Formatted markdown output
  - Downloadable content
  - Syntax highlighting

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

## Project Structure

```
github_stitcher/
├── app.py                # Main Streamlit application
├── config.py            # Configuration settings
├── github/              # GitHub interaction modules
│   ├── api.py          # Main GitHub API interface
│   ├── parsers.py      # URL parsing utilities
│   └
```
