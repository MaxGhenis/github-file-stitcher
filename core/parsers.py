import re
from typing import Tuple, Optional, Union


def normalize_github_url(url: str) -> str:
    """Normalize GitHub URLs to ensure they start with https://"""
    if url.startswith(("github.com/", "github.com")):
        return "https://" + url.lstrip("/")
    return url


def parse_github_input(
    input_line: str,
) -> Tuple[
    Optional[str], Optional[str], Optional[Union[str, Tuple[str, str]]]
]:
    """Parse GitHub URLs and regex patterns into their components."""
    print(f"Parsing input: {input_line}")  # Debug line

    # Handle regex patterns
    if input_line.startswith("regex:"):
        return "regex", None, input_line[6:].strip()

    # Normalize the URL
    input_line = normalize_github_url(input_line)
    print(f"Normalized URL: {input_line}")  # Debug line

    patterns = {
        "issue": (
            r"(?:https://)?github\.com/([^/]+/[^/]+)/issues/(\d+)",
            lambda m: ("issue", m.group(1), m.group(2)),
        ),
        "pr": (
            r"(?:https://)?github\.com/([^/]+/[^/]+)/pull/(\d+)",
            lambda m: ("pr", m.group(1), m.group(2)),
        ),
        "repo": (
            r"(?:https://)?github\.com/([^/]+/[^/]+)/?$",
            lambda m: ("repo", m.group(1), None),
        ),
        "file": (
            r"(?:https://)?github\.com/([^/]+/[^/]+)/blob/([^/]+)/(.+)",
            lambda m: ("file", m.group(1), (m.group(3), m.group(2))),
        ),
        "content": (
            r"(?:https://)?github\.com/([^/]+/[^/]+)(?:/tree/([^/]+))?(/.+)?",
            lambda m: ("content", m.group(1), (m.group(3) or "", m.group(2))),
        ),
    }

    for pattern_name, (regex, handler) in patterns.items():
        print(f"Trying {pattern_name} pattern")  # Debug line
        match = re.match(regex, input_line)
        if match:
            result = handler(match)
            print(f"Matched {pattern_name}: {result}")  # Debug line
            return result

    print("No pattern matched")  # Debug line
    return None, None, None
