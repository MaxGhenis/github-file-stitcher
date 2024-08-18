import re
import base64


def parse_github_input(input_line):
    pr_match = re.match(
        r"https://github.com/([^/]+/[^/]+)/pull/(\d+)", input_line
    )
    if pr_match:
        return "pr", pr_match.group(1), pr_match.group(2)

    if input_line.startswith("regex:"):
        return "regex", None, input_line[6:].strip()

    repo_match = re.match(r"https://github.com/([^/]+/[^/]+)/?$", input_line)
    if repo_match:
        return "repo", repo_match.group(1), None

    match = re.match(
        r"https://github.com/([^/]+/[^/]+)(?:/tree/([^/]+))?(/.*)?", input_line
    )
    if match:
        repo_name = match.group(1)
        branch = match.group(2)
        path = match.group(3) or ""
        return "content", repo_name, (path.lstrip("/"), branch)

    return None, None, None


def get_file_content(
    repo, file_path, regex_patterns, keep_matching, branch=None
):
    try:
        if branch is None:
            branch = repo.default_branch
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
