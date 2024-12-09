from typing import Optional, List
from .base import ContentProcessor


class IssueProcessor(ContentProcessor):
    def process(
        self,
        repo_name: str,
        issue_number: str,
        file_patterns: Optional[List[str]] = None,
        keep_matching_files: bool = True,
        line_patterns: Optional[List[str]] = None,
        keep_matching_lines: bool = True,
        **kwargs,
    ) -> str:
        """Process a GitHub issue and its comments into markdown format."""
        try:
            print(
                f"Processing issue: repo={repo_name}, issue={issue_number}"
            )  # Debug line
            repo = self.get_repo(repo_name)
            issue = repo.get_issue(int(issue_number))

            content = []
            # Add issue header
            content.extend(
                [
                    f"# {issue.title}\n",
                    f"**Author:** {issue.user.login}  \n",
                    f"**Created:** {issue.created_at}  \n",
                    f"**State:** {issue.state}  \n\n",
                    "## Original Post\n\n",
                    issue.body or "*No description provided*",
                    "\n\n---\n\n",
                    "## Comments\n\n",
                ]
            )

            # Add comments
            for comment in issue.get_comments():
                content.extend(
                    [
                        f"### {comment.user.login} - {comment.created_at}\n\n",
                        f"{comment.body}\n\n",
                        "---\n\n",
                    ]
                )

            return "".join(content)
        except Exception as e:
            print(f"Error in IssueProcessor: {str(e)}")  # Debug line
            raise
