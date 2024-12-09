import re
import base64
from typing import List, Union, Optional
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
        repo = self.get_repo(repo_name)

        # Handle different input types
        if isinstance(extra_info, tuple):  # File or content path
            path, branch = extra_info
            branch = branch or repo.default_branch
            contents = [repo.get_contents(path, ref=branch)]
        else:  # Repository root
            branch = repo.default_branch
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

    def _process_contents(
        self,
        repo: Repository,
        contents: List[ContentFile],
        branch: str,
        file_patterns: Optional[List[str]],
        keep_matching_files: bool,
        line_patterns: Optional[List[str]],
        keep_matching_lines: bool,
    ) -> str:
        """Process list of content files recursively."""
        result = []
        if not isinstance(contents, list):
            contents = [contents]

        while contents:
            content = contents.pop(0)

            # Handle directories recursively
            if content.type == "dir":
                dir_contents = repo.get_contents(content.path, ref=branch)
                contents.extend(dir_contents)
                continue

            # Check if file matches patterns
            if not self._should_include_file(
                content.path, file_patterns, keep_matching_files
            ):
                continue

            # Process the file
            file_content = self._get_file_content(
                repo, content, branch, line_patterns, keep_matching_lines
            )

            if file_content:
                result.extend(
                    [f"\n--- {content.path} ---\n\n", file_content, "\n"]
                )

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
            file_content = base64.b64decode(content.content).decode(
                "utf-8", errors="replace"
            )

            # Apply line filtering if patterns are provided
            if line_patterns:
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

    def _should_include_file(
        self,
        file_path: str,
        patterns: Optional[List[str]],
        keep_matching: bool,
    ) -> bool:
        """Determine if a file should be included based on patterns."""
        if not patterns:
            return True

        matches = any(re.search(pattern, file_path) for pattern in patterns)
        return matches == keep_matching

    def _should_include_line(
        self, line: str, patterns: List[str], keep_matching: bool
    ) -> bool:
        """Determine if a line should be included based on patterns."""
        matches = any(re.search(pattern, line) for pattern in patterns)
        return matches == keep_matching
