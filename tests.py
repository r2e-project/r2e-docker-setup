import os
import sys

from paths import REPOS_DIR, PDM_BIN_DIR
from multiprocess_utils import run_tasks_in_parallel_iter
from bash_utils import run_subprocess_shell
from install_single_repo import install_single_repo

# 1. Check that every folder in REPOS_DIR has a .venv
def test_venvs():
    bad_repos = []
    repos = os.listdir(REPOS_DIR)
    for repo in repos:
        venv = os.path.join(REPOS_DIR, repo, '.venv')
        #print(f"Testing repo {repo} for venv...")
        if not os.path.exists(venv):
            bad_repos.append(repo)
    return bad_repos

if __name__ == '__main__':
    # Test that all virtual environments were added successfully
    print("Running venv installation test...")
    bad_repos = test_venvs()
    if bad_repos:
        print(f"venv installation failed for the following repos: {bad_repos}")
    else:
        print("venv test passed successfully")

