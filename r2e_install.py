import os

from paths import REPOS_DIR
from bash_utils import run_subprocess_shell
from multiprocess_utils import run_tasks_in_parallel_iter


def single_server_install(repo_name: str):
    run_subprocess_shell(
        f"cd {REPOS_DIR}/{repo_name} && .venv/bin/python -m pip install r2e_test_server"
    )


def r2e_server_install(all_repos):

    outputs = run_tasks_in_parallel_iter(
        single_server_install,
        all_repos,
        num_workers=8,
        use_progress_bar=True,
    )

    for output in outputs:
        if output.is_success():
            pass
        else:
            print(output.exception_tb)


if __name__ == "__main__":
    all_repos = sorted(os.listdir(REPOS_DIR))
    r2e_server_install(all_repos)
