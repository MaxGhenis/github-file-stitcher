import re
from typing import Tuple, Optional, Union


def normalize_github_url(url: str) -> str:
    """Normalize GitHub URLs to ensure they start with https://"""
    if url.startswith(("github.com/", "github.com")):
        normalized = "https://" + url.lstrip("/")
        print(f"DEBUG: Normalized URL from '{url}' to '{normalized}'")
        return normalized
    return url


def clean_name(name: str) -> str:
    """Clean name by removing trailing slashes and extra spaces."""
    return name.rstrip("/").strip()


def parse_github_input(
    input_line: str,
) -> Tuple[
    Optional[str], Optional[str], Optional[Union[str, Tuple[str, str]]]
]:
    """Parse GitHub URLs and regex patterns into their components."""
    print(f"\nDEBUG: Starting to parse input: '{input_line}'")

    # Handle regex patterns
    if input_line.startswith("regex:"):
        print("DEBUG: Detected regex pattern")
        return "regex", None, input_line[6:].strip()

    # Normalize the URL
    input_line = normalize_github_url(input_line)

    # First match repository and get remaining part
    repo_pattern = r"(?:https://)?github\.com/([^/]+/[^/]+)"
    repo_match = re.match(repo_pattern, input_line)
    if not repo_match:
        print("DEBUG: Failed to match repository pattern")
        return None, None, None

    repo_name = repo_match.group(1)
    remaining = input_line[repo_match.end() :]
    print(f"DEBUG: Matched repository: {repo_name}")
    print(f"DEBUG: Remaining URL part: {remaining}")

    # Handle tree URLs (directories)
    if remaining.startswith("/tree/"):
        print("DEBUG: Processing tree URL")
        parts = parse_ref_path(remaining[6:])  # Skip /tree/
        if parts:
            branch, path = parts
            return "content", repo_name, (path, branch)

    # Handle blob URLs (files)
    elif remaining.startswith("/blob/"):
        print("DEBUG: Processing blob URL")
        parts = parse_ref_path(remaining[6:])  # Skip /blob/
        if parts:
            branch, path = parts
            return "file", repo_name, (path, branch)

    # Handle other URL types
    elif remaining == "" or remaining == "/":
        return "repo", repo_name, None
    elif remaining.startswith("/pull/"):
        pr_num = remaining[6:].strip("/")
        return "pr", repo_name, pr_num
    elif remaining.startswith("/issues/"):
        issue_num = remaining[8:].strip("/")
        return "issue", repo_name, issue_num

    print("DEBUG: No pattern matched")
    return None, None, None


def parse_ref_path(ref_path: str) -> Optional[Tuple[str, str]]:
    """Parse a reference (branch/tag) and path from a GitHub URL component.

    Args:
        ref_path: The part of the URL after /tree/ or /blob/

    Returns:
        Tuple of (branch, path) if successful, None if not
    """
    if not ref_path:
        return None

    ref_path = ref_path.rstrip("/")
    print(f"DEBUG: Parsing ref_path: {ref_path}")

    # Find the first real path separator after the ref
    parts = ref_path.split("/")
    if not parts:
        return None

    # First component is always the branch/tag name
    branch = parts[0]

    # Rest is the path (if any)
    path = "/".join(parts[1:]) if len(parts) > 1 else ""

    print(f"DEBUG: Parsed branch: '{branch}', path: '{path}'")
    return branch, path
