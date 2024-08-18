import re
import requests
from github import Github, GithubException
from io import StringIO
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

    file_match = re.match(
        r"https://github.com/([^/]+/[^/]+)/blob/([^/]+)/(.+)", input_line
    )
    if file_match:
        return (
            "file",
            file_match.group(1),
            (file_match.group(3), file_match.group(2)),
        )

    content_match = re.match(
        r"https://github.com/([^/]+/[^/]+)(?:/tree/([^/]+))?(/.*)?", input_line
    )
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


def process_github_content(g, inputs, regex_patterns, keep_matching):
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
                diff = get_pr_diff(owner, repo, extra_info, github_token)
                output.write(diff)
            elif input_type in ["content", "repo", "file"]:
                repo = g.get_repo(repo_name)
                if input_type == "repo":
                    contents = repo.get_contents(
                        "", ref=get_default_branch(repo)
                    )
                    branch = get_default_branch(repo)
                elif input_type == "file":
                    file_path, branch = extra_info
                    contents = [repo.get_contents(file_path, ref=branch)]
                else:
                    path, branch = extra_info
                    branch = branch or get_default_branch(repo)
                    contents = repo.get_contents(path, ref=branch)

                if not isinstance(contents, list):
                    contents = [contents]

                while contents:
                    file_content = contents.pop(0)
                    if file_content.type == "dir":
                        contents.extend(
                            repo.get_contents(file_content.path, ref=branch)
                        )
                    else:
                        output.write(f"\n--- {file_content.path} ---\n\n")
                        content = get_file_content(
                            repo,
                            file_content.path,
                            regex_patterns,
                            keep_matching,
                            branch,
                        )
                        output.write(content)
                        output.write("\n")
            elif input_type == "regex":
                for repo in g.get_user().get_repos():
                    default_branch = get_default_branch(repo)
                    for content in repo.get_contents("", ref=default_branch):
                        if re.match(extra_info, content.path):
                            output.write(
                                f"\n--- {repo.full_name}/{content.path} ---\n\n"
                            )
                            content = get_file_content(
                                repo,
                                content.path,
                                regex_patterns,
                                keep_matching,
                                default_branch,
                            )
                            output.write(content)
                            output.write("\n")
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
