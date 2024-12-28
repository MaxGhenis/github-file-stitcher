from typing import List, Union, Optional
import urllib.parse
from github import Github
from github.ContentFile import ContentFile
from github.Repository import Repository
from .base import ContentProcessor
from ..config import GITHUB_MAX_FILE_SIZE, BINARY_FILE_EXTENSIONS


class RepoProcessor(ContentProcessor):
    def process(
        self,
        repo_name: str,
        extra_info: Optional[Union[str, tuple]],
        file_patterns: Optional[List[str]] = None,
        keep_matching_files: bool = True,
        line_patterns: Optional[List[str]] = None,
        keep_matching_lines: bool = True,
        **kwargs,
    ) -> str:
        """Process repository contents with file and line filtering."""
        try:
            print(f"\nDEBUG: Processing repository: {repo_name}")
            print(f"DEBUG: Extra info: {extra_info}")

            repo = self.get_repo(repo_name)
            print(f"DEBUG: Default branch: {repo.default_branch}")

            # Handle different input types
            if isinstance(extra_info, tuple):
                path, branch = extra_info
                print(f"DEBUG: Raw path: '{path}', branch: '{branch}'")

                if branch:
                    # Don't URL encode the branch name yet
                    print(f"DEBUG: Using specified branch: '{branch}'")
                else:
                    branch = repo.default_branch
                    print(f"DEBUG: Using default branch: '{branch}'")

                try:
                    if path:
                        print(
                            f"DEBUG: Fetching specific path: '{path}' from branch: '{branch}'"
                        )
                        contents = repo.get_contents(path, ref=branch)
                    else:
                        print(
                            f"DEBUG: Fetching root contents from branch: '{branch}'"
                        )
                        contents = repo.get_contents("", ref=branch)
                    print("DEBUG: Successfully fetched contents")

                except Exception as e:
                    error_msg = f"Error fetching content from branch '{branch}': {str(e)}"
                    print(f"DEBUG: {error_msg}")
                    return error_msg
            else:
                branch = repo.default_branch
                print(
                    f"DEBUG: Using default branch (no extra info): '{branch}'"
                )
                contents = repo.get_contents("", ref=branch)

            return self._process_contents(
                repo,
                contents,
                branch,
                file_patterns,
                keep_matching_files,
                line_patterns,
                keep_matching_lines,
            )

        except Exception as e:
            error_msg = f"Error processing repository: {str(e)}"
            print(f"DEBUG: {error_msg}")
            return error_msg

    def _process_contents(
        self,
        repo: Repository,
        contents: Union[List[ContentFile], ContentFile],
        branch: str,
        file_patterns: Optional[List[str]],
        keep_matching_files: bool,
        line_patterns: Optional[List[str]],
        keep_matching_lines: bool,
    ) -> str:
        """Process list of content files recursively."""
        print(f"\nDEBUG: Processing contents for branch: '{branch}'")

        result = []
        if not isinstance(contents, list):
            contents = [contents]

        while contents:
            content = contents.pop(0)
            try:
                print(f"\nDEBUG: Processing content: {content.path}")

                # Handle directories recursively
                if content.type == "dir":
                    print(f"DEBUG: Found directory: {content.path}")
                    dir_contents = repo.get_contents(content.path, ref=branch)
                    if isinstance(dir_contents, list):
                        contents.extend(dir_contents)
                    else:
                        contents.append(dir_contents)
                    continue

                # Process the file
                file_content = self._get_file_content(
                    repo, content, branch, line_patterns, keep_matching_lines
                )

                if file_content:
                    result.extend(
                        [f"\n--- {content.path} ---\n\n", file_content, "\n"]
                    )

            except Exception as e:
                error_msg = f"\nError processing {content.path}: {str(e)}\n"
                print(f"DEBUG: {error_msg}")
                result.append(error_msg)

        return "".join(result)

    def _get_file_content(
        self,
        repo: Repository,
        content: ContentFile,
        branch: str,
        line_patterns: Optional[List[str]],
        keep_matching_lines: bool,
    ) -> Optional[str]:
        """Get and process content of a single file."""
        try:
            # Check file size
            if content.size > GITHUB_MAX_FILE_SIZE:
                return f"File is too large to display (size: {content.size} bytes)"

            # Handle binary files
            file_ext = content.path.split(".")[-1].lower()
            for type_name, extensions in BINARY_FILE_EXTENSIONS.items():
                if file_ext in extensions:
                    return f"[Binary {type_name} file: {content.path}]"

            # Decode content
            file_content = self._decode_content(content)

            # Apply line filtering if patterns are provided
            if line_patterns and file_content:
                lines = file_content.split("\n")
                lines = [
                    line
                    for line in lines
                    if self._should_include_line(
                        line, line_patterns, keep_matching_lines
                    )
                ]
                return "\n".join(lines)

            return file_content

        except Exception as e:
            return (
                f"Error: Could not fetch content for {content.path}. {str(e)}"
            )

    def _decode_content(self, content: ContentFile) -> str:
        """Safely decode content from base64."""
        try:
            import base64

            return base64.b64decode(content.content).decode(
                "utf-8", errors="replace"
            )
        except Exception as e:
            return f"Error decoding content: {str(e)}"

    def _should_include_line(
        self, line: str, patterns: List[str], keep_matching: bool
    ) -> bool:
        """Determine if a line should be included based on patterns."""
        import re

        matches = any(re.search(pattern, line) for pattern in patterns)
        return matches == keep_matching
