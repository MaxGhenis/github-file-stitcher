import streamlit as st
import re
import requests
from github import Github, GithubException
from io import StringIO


def parse_github_input(input_line):
    pr_match = re.match(
        r"https://github.com/([^/]+/[^/]+)/pull/(\d+)", input_line
    )
    if pr_match:
        return "pr", pr_match.group(1), pr_match.group(2)

    if input_line.startswith("regex:"):
        return "regex", None, input_line[6:].strip()

    match = re.match(
        r"https://github.com/([^/]+/[^/]+)(?:/tree/([^/]+))?(/.*)?", input_line
    )
    if match:
        repo_name = match.group(1)
        branch = match.group(2) or "master"
        path = match.group(3) or ""
        return "content", repo_name, (path.lstrip("/"), branch)

    return None, None, None


def get_file_content(
    repo, file_path, regex_patterns, keep_matching, branch="master"
):
    try:
        file_content = repo.get_contents(
            file_path, ref=branch
        ).decoded_content.decode("utf-8")
        lines = file_content.split("\n")
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
            return file_content
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
    github_token = st.secrets["GITHUB_TOKEN"]

    for input_line in inputs:
        input_type, repo_name, extra_info = parse_github_input(input_line)

        if input_type is None:
            output.write(f"\nInvalid input: {input_line}\n")
            continue

        output.write(f"\n\n--- Content from {input_line} ---\n")
        try:
            if input_type == "pr":
                owner, repo = repo_name.split("/")
                diff = get_pr_diff(owner, repo, extra_info, github_token)
                output.write(diff)
            elif input_type == "content":
                repo = g.get_repo(repo_name)
                path, branch = extra_info
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
                    for content in repo.get_contents(""):
                        if re.match(extra_info, content.path):
                            output.write(
                                f"\n--- {repo.full_name}/{content.path} ---\n\n"
                            )
                            content = get_file_content(
                                repo,
                                content.path,
                                regex_patterns,
                                keep_matching,
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
        except Exception as e:
            output.write(f"An error occurred: {str(e)}\n")
    return output.getvalue()


def main():
    st.set_page_config(
        page_title="GitHub Stitcher", page_icon="🧵", layout="wide"
    )

    st.title("🧵 GitHub Stitcher")
    st.markdown(
        """
    Stitch together content from GitHub repositories or fetch PR diffs. 
    Enter URLs to files, folders, PRs, or use regex patterns to match file paths.
    Filter content using regex patterns to keep or omit specific lines.
    """
    )

    # Use GitHub token from Streamlit secrets
    github_token = st.secrets["GITHUB_TOKEN"]

    # Input for GitHub URLs and regex patterns
    github_inputs = st.text_area(
        "Enter GitHub URLs, PR links, or regex patterns (one per line):",
        height=150,
        help="Enter URLs to files, folders, PRs, or use 'regex:' prefix for file path patterns. "
        "e.g., https://github.com/username/repo/tree/branch/folder, "
        "https://github.com/username/repo/pull/123, or regex:.*\\.py$",
    )

    # Input for text filtering
    regex_patterns = st.text_area(
        "Enter regex patterns for text filtering (one per line):",
        height=100,
        help="These patterns will be used to filter the content of the files. Leave empty to include all content.",
    )

    # Radio button to choose between keeping or omitting matched lines
    filter_mode = st.radio(
        "Choose filtering mode:",
        ("Keep matching lines", "Omit matching lines"),
        help="Select whether to keep or omit the lines that match the regex patterns above.",
    )

    if st.button(
        "🧵 Stitch Content", help="Click to fetch and stitch the content"
    ):
        if not github_inputs:
            st.warning(
                "⚠️ Please enter at least one GitHub URL, PR link, or regex pattern."
            )
            return

        inputs = [
            line.strip() for line in github_inputs.split("\n") if line.strip()
        ]
        patterns = [
            pattern.strip()
            for pattern in regex_patterns.split("\n")
            if pattern.strip()
        ]
        keep_matching = filter_mode == "Keep matching lines"

        with st.spinner("Fetching and stitching content..."):
            g = Github(github_token)
            all_content = process_github_content(
                g, inputs, patterns, keep_matching
            )

            if "Error:" in all_content:
                st.error(
                    "⚠️ Some errors occurred while fetching content. Please check the output below."
                )
            else:
                st.success("✅ Content stitched successfully!")

            st.subheader("Stitched Content:")
            st.code(all_content, language="text")

            st.download_button(
                "💾 Download Stitched Content",
                all_content,
                "stitched_content.txt",
                help="Click to download the stitched content as a text file",
            )

    st.sidebar.title("About")
    st.sidebar.info(
        """
        GitHub Stitcher was created by [Max Ghenis](mailto:mghenis@gmail.com).

        This tool allows you to:
        - Fetch content from GitHub files, folders, or entire repositories
        - Fetch diffs from Pull Requests
        - Use regex patterns to filter specific file paths
        - Keep or omit lines based on regex patterns
        - Combine the filtered content into a single, easy-to-use output
        """
    )


if __name__ == "__main__":
    main()
