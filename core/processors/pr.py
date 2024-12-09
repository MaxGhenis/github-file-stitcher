import requests
from typing import Optional, List
from .base import ContentProcessor


class PRProcessor(ContentProcessor):
    def process(
        self,
        repo_name: str,
        pull_number: str,
        file_patterns: Optional[List[str]] = None,
        keep_matching_files: bool = True,
        line_patterns: Optional[List[str]] = None,
        keep_matching_lines: bool = True,
        **kwargs,
    ) -> str:
        """Process a pull request and return its diff."""
        owner, repo = repo_name.split("/")
        diff = self._get_pr_diff(owner, repo, pull_number)

        if diff.startswith("Error"):
            return diff

        # Add PR metadata before the diff
        pr = self.get_repo(repo_name).get_pull(int(pull_number))
        metadata = [
            f"# Pull Request #{pull_number}: {pr.title}\n",
            f"**Author:** {pr.user.login}  \n",
            f"**Created:** {pr.created_at}  \n",
            f"**State:** {pr.state}  \n",
            f"**Base:** {pr.base.ref} ← **Head:** {pr.head.ref}  \n\n",
            "## Description\n\n",
            pr.body or "*No description provided*",
            "\n\n## Changes\n\n```diff\n",
            diff,
            "\n```",
        ]

        return "".join(metadata)

    def _get_pr_diff(self, owner: str, repo: str, pull_number: str) -> str:
        """Fetch the diff for a pull request."""
        token = self.github._Github__requester._Requester__auth.token
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
        )
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3.diff",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching PR diff: {response.status_code}"
