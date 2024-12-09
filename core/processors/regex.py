import re
from typing import List, Optional
from .base import ContentProcessor
from .repo import RepoProcessor


class RegexProcessor(ContentProcessor):
    def process(
        self,
        repo_name: None,
        pattern: str,
        file_patterns: Optional[List[str]] = None,
        keep_matching_files: bool = True,
        line_patterns: Optional[List[str]] = None,
        keep_matching_lines: bool = True,
        **kwargs,
    ) -> str:
        """Process content matching regex pattern across user's repositories."""
        repo_processor = RepoProcessor(self.github)
        results = []

        # Search through all user's repositories
        for repo in self.github.get_user().get_repos():
            try:
                # Get root contents
                contents = repo.get_contents("", ref=repo.default_branch)

                # Filter contents by regex pattern
                matching_contents = []
                while contents:
                    content = contents.pop(0)
                    if content.type == "dir":
                        contents.extend(
                            repo.get_contents(
                                content.path, ref=repo.default_branch
                            )
                        )
                    elif re.match(pattern, content.path):
                        matching_contents.append(content)

                # Process matching contents
                if matching_contents:
                    content = repo_processor._process_contents(
                        repo,
                        matching_contents,
                        repo.default_branch,
                        file_patterns,
                        keep_matching_files,
                        line_patterns,
                        keep_matching_lines,
                    )
                    if content:
                        results.extend(
                            [f"\n### Repository: {repo.full_name}\n", content]
                        )

            except Exception as e:
                results.append(
                    f"\nError processing {repo.full_name}: {str(e)}\n"
                )

        return "".join(results) if results else "No matching files found."
