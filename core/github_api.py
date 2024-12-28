from typing import List, Tuple, Optional
from io import StringIO
from github import Github
from github.GithubException import GithubException

from .parsers import parse_github_input
from .processors.issue import IssueProcessor
from .processors.pr import PRProcessor
from .processors.repo import RepoProcessor
from .processors.regex import RegexProcessor


class GitHubAPI:
    def __init__(self, token: str):
        self.github = Github(token)
        self.processors = {
            "issue": IssueProcessor(self.github),
            "pr": PRProcessor(self.github),
            "repo": RepoProcessor(self.github),
            "regex": RegexProcessor(self.github),
            # Add file type but use the same RepoProcessor since it can handle both files and directories
            "file": RepoProcessor(self.github),
            "content": RepoProcessor(self.github),
        }

    def process_content(
        self,
        inputs: List[str],
        file_patterns: List[str],
        keep_matching_files: bool,
        line_patterns: Optional[List[str]] = None,
        keep_matching_lines: bool = True,
    ) -> Tuple[str, bool]:
        """Process GitHub content with file and line filtering."""
        output = StringIO()
        error_occurred = False

        for input_line in inputs:
            input_type, repo_name, extra_info = parse_github_input(input_line)
            print(
                f"Parsed input: type={input_type}, repo={repo_name}, extra={extra_info}"
            )

            if input_type is None:
                output.write(f"\nInvalid input: {input_line}\n")
                error_occurred = True
                continue

            output.write(f"\n\n--- Content from {input_line} ---\n")

            try:
                processor = self.processors.get(input_type)
                if processor:
                    print(f"Using processor: {processor.__class__.__name__}")
                    content = processor.process(
                        repo_name,
                        extra_info,
                        file_patterns=file_patterns,
                        keep_matching_files=keep_matching_files,
                        line_patterns=line_patterns,
                        keep_matching_lines=keep_matching_lines,
                    )
                    output.write(content)
                else:
                    output.write(f"Unsupported input type: {input_type}\n")
                    error_occurred = True

            except GithubException as e:
                error_msg = self._handle_github_exception(e)
                print(f"GitHub Exception: {error_msg}")
                output.write(error_msg)
                error_occurred = True
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                output.write(f"An error occurred: {str(e)}\n")
                error_occurred = True

        return output.getvalue(), error_occurred

    def _handle_github_exception(self, e: GithubException) -> str:
        if e.status == 404:
            return (
                "Error: Repository, path, PR, or issue not found. "
                "Please check the URL and ensure you have access.\n"
            )
        return f"GitHub API error: {e.status} - {e.data.get('message', 'Unknown error')}\n"
