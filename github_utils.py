import re
import requests
from github import Github, GithubException
from io import StringIO
import base64


def normalize_github_url(url):
    """Normalize GitHub URLs to ensure they start with https://"""
    if url.startswith(("github.com/", "github.com")):
        return "https://" + url.lstrip("/")
    return url


def parse_github_input(input_line):
    """Parse GitHub URLs and regex patterns into their components."""
    # Handle regex patterns first since they shouldn't be normalized
    if input_line.startswith("regex:"):
        return "regex", None, input_line[6:].strip()

    # Normalize the URL if it starts with github.com
    input_line = normalize_github_url(input_line)

    # Common URL patterns with or without https://
    # PR pattern
    pr_pattern = r"(?:https://)?github\.com/([^/]+/[^/]+)/pull/(\d+)"
    pr_match = re.match(pr_pattern, input_line)
    if pr_match:
        return "pr", pr_match.group(1), pr_match.group(2)

    # Repository root pattern
    repo_pattern = r"(?:https://)?github\.com/([^/]+/[^/]+)/?$"
    repo_match = re.match(repo_pattern, input_line)
    if repo_match:
        return "repo", repo_match.group(1), None

    # File pattern
    file_pattern = r"(?:https://)?github\.com/([^/]+/[^/]+)/blob/([^/]+)/(.+)"
    file_match = re.match(file_pattern, input_line)
    if file_match:
        return (
            "file",
            file_match.group(1),
            (file_match.group(3), file_match.group(2)),
        )

    # Content/tree pattern
    content_pattern = (
        r"(?:https://)?github\.com/([^/]+/[^/]+)(?:/tree/([^/]+))?(/.*)?"
    )
    content_match = re.match(content_pattern, input_line)
    if content_match:
        repo_name = content_match.group(1)
        branch = content_match.group(2)
        path = content_match.group(3) or ""
        return "content", repo_name, (path.lstrip("/"), branch)

    return None, None, None


def get_default_branch(repo):
    return repo.default_branch


def get_file_content(
    repo, file_path, regex_patterns, keep_matching, branch=None
):
    try:
        if branch is None:
            branch = get_default_branch(repo)
        file_content = repo.get_contents(file_path, ref=branch)

        # Check if the file is too large (over 1MB)
        if file_content.size > 1000000:
            return f"File {file_path} is too large to display (size: {file_content.size} bytes)"

        # Handle binary files
        file_type = file_path.split(".")[-1].lower()
        if file_type in ["png", "jpg", "jpeg", "gif", "bmp"]:
            return f"[Binary image file: {file_path}]"
        elif file_type in ["pdf", "doc", "docx", "xls", "xlsx"]:
            return f"[Binary document file: {file_path}]"

        # Decode content for text files
        content = base64.b64decode(file_content.content).decode(
            "utf-8", errors="replace"
        )

        lines = content.split("\n")
        if regex_patterns:
            if keep_matching:
                return "\n".join(
                    line
                    for line in lines
                    if any(
                        re.search(pattern, line) for pattern in regex_patterns
                    )
                )
            else:
                return "\n".join(
                    line
                    for line in lines
                    if not any(
                        re.search(pattern, line) for pattern in regex_patterns
                    )
                )
        else:
            return content
    except Exception as e:
        return f"Error: Could not fetch content for {file_path}. {str(e)}"


def get_pr_diff(owner, repo, pull_number, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error fetching GitHub diff: {response.status_code}"


def process_pr_content(owner, repo, pull_number, github_token):
    """Process pull request content and return the diff."""
    diff = get_pr_diff(owner, repo, pull_number, github_token)
    return diff


def process_file_content(
    repo, file_content, branch, line_patterns, keep_matching_lines
):
    """Process individual file content with line filtering."""
    content = get_file_content(
        repo,
        file_content.path,
        line_patterns,
        keep_matching_lines,
        branch,
    )
    return f"\n--- {file_content.path} ---\n\n{content}\n"


def should_include_file(file_path, file_patterns, keep_matching_files):
    """Determine if a file should be included based on pattern matching."""
    if not file_patterns:
        return True
    file_matches = any(
        re.search(pattern, file_path) for pattern in file_patterns
    )
    return file_matches == keep_matching_files


def process_repo_contents(
    repo,
    contents,
    branch,
    file_patterns,
    keep_matching_files,
    line_patterns,
    keep_matching_lines,
):
    """Process repository contents with file and line filtering."""
    output = StringIO()
    if not isinstance(contents, list):
        contents = [contents]

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path, ref=branch))
        elif should_include_file(
            file_content.path, file_patterns, keep_matching_files
        ):
            content = process_file_content(
                repo, file_content, branch, line_patterns, keep_matching_lines
            )
            output.write(content)

    return output.getvalue()


def process_regex_content(
    g,
    pattern,
    file_patterns,
    keep_matching_files,
    line_patterns,
    keep_matching_lines,
):
    """Process content matching regex pattern across user's repositories."""
    output = StringIO()
    for repo in g.get_user().get_repos():
        default_branch = get_default_branch(repo)
        for content in repo.get_contents("", ref=default_branch):
            if re.match(pattern, content.path) and should_include_file(
                content.path, file_patterns, keep_matching_files
            ):
                content_str = process_file_content(
                    repo,
                    content,
                    default_branch,
                    line_patterns,
                    keep_matching_lines,
                )
                output.write(f"\n{repo.full_name}/{content_str}")

    return output.getvalue()


def process_github_content(
    g,
    inputs,
    file_patterns,
    keep_matching_files,
    line_patterns=None,
    keep_matching_lines=True,
):
    """
    Process GitHub content with separate file and line pattern filtering.

    Args:
        g: Github instance
        inputs: List of GitHub URLs/inputs to process
        file_patterns: List of regex patterns for filtering files
        keep_matching_files: Boolean to keep or exclude matching files
        line_patterns: List of regex patterns for filtering lines within files
        keep_matching_lines: Boolean to keep or exclude matching lines
    """
    output = StringIO()
    github_token = g._Github__requester._Requester__auth.token
    error_occurred = False

    for input_line in inputs:
        input_type, repo_name, extra_info = parse_github_input(input_line)

        if input_type is None:
            output.write(f"\nInvalid input: {input_line}\n")
            error_occurred = True
            continue

        output.write(f"\n\n--- Content from {input_line} ---\n")
        try:
            if input_type == "pr":
                owner, repo = repo_name.split("/")
                content = process_pr_content(
                    owner, repo, extra_info, github_token
                )
                output.write(content)

            elif input_type in ["content", "repo", "file"]:
                repo = g.get_repo(repo_name)
                branch = get_default_branch(repo)

                if input_type == "repo":
                    contents = repo.get_contents("", ref=branch)
                elif input_type == "file":
                    file_path, branch = extra_info
                    contents = [repo.get_contents(file_path, ref=branch)]
                else:
                    path, branch = extra_info
                    branch = branch or get_default_branch(repo)
                    contents = repo.get_contents(path, ref=branch)

                content = process_repo_contents(
                    repo,
                    contents,
                    branch,
                    file_patterns,
                    keep_matching_files,
                    line_patterns,
                    keep_matching_lines,
                )
                output.write(content)

            elif input_type == "regex":
                content = process_regex_content(
                    g,
                    extra_info,
                    file_patterns,
                    keep_matching_files,
                    line_patterns,
                    keep_matching_lines,
                )
                output.write(content)

        except GithubException as e:
            if e.status == 404:
                output.write(
                    f"Error: Repository, path, or PR not found. Please check the URL and ensure you have access to this repository.\n"
                )
            else:
                output.write(
                    f"GitHub API error: {e.status} - {e.data.get('message', 'Unknown error')}\n"
                )
            error_occurred = True
        except Exception as e:
            output.write(f"An error occurred: {str(e)}\n")
            error_occurred = True

    return output.getvalue(), error_occurred
