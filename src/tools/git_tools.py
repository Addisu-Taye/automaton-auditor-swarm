import os
import tempfile
from typing import List, Dict
from git import Repo


def clone_repo_sandboxed(repo_url: str) -> str:
    """
    Security Protocol: Never clone into working directory.
    Uses tempfile.TemporaryDirectory() for isolation.
    """
    temp_dir = tempfile.TemporaryDirectory()
    try:
        Repo.clone_from(repo_url, temp_dir.name)
        return temp_dir.name
    except Exception as e:
        raise Exception(f"Git Clone Failed: {str(e)}")


def get_git_history(repo_path: str) -> List[Dict]:
    """
    Forensic Protocol: Extract atomic commit history.
    Detects bulk upload vs iterative development.
    """
    try:
        repo = Repo(repo_path)
        commits = []
        for commit in repo.iter_commits():
            commits.append({
                "hash": commit.hexsha,
                "message": commit.message.strip(),
                "timestamp": commit.committed_datetime.isoformat(),
                "author": str(commit.author)
            })
        return commits
    except Exception as e:
        return [{"error": str(e)}]
