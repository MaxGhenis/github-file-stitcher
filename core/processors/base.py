from abc import ABC, abstractmethod
from typing import List, Optional
from github import Github
from github.Repository import Repository


class ContentProcessor(ABC):
    def __init__(self, github_client: Github):
        self.github = github_client

    @abstractmethod
    def process(self, repo_name: str, extra_info: any) -> str:
        pass

    def get_repo(self, repo_name: str) -> Repository:
        return self.github.get_repo(repo_name)
