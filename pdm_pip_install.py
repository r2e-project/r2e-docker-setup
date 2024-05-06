import os
from logging import Logger
from subprocess import CompletedProcess

from paths import REPOS_DIR, PDM_BIN_DIR
from bash_utils import run_subprocess_shell
from toml_updator import PyprojectTomlUpdater

BUILD_TRIES = 3


def pdm_build_repo(
    repo_name: str,
    ptu: PyprojectTomlUpdater,
    repo_logger: Logger,
    *,
    current_try: int,
) -> CompletedProcess[str]:
    repo_logger.info(f"Building {repo_name}... ({current_try + 1}/{BUILD_TRIES})")

    result = run_subprocess_shell(
        f"export PATH={PDM_BIN_DIR} \
                && cd {REPOS_DIR}/{repo_name} \
                && pdm install \
            ",
        repo_logger,
        timeout=60 * 10,
    )
    if result.stdout:
        repo_logger.info(result.stdout)
    if result.stderr:
        repo_logger.warning(result.stderr)
    if result.returncode != 0:
        repo_logger.error(
            f"Failed to build {repo_name} ({current_try + 1}/{BUILD_TRIES})"
        )

    return result


def pdm_reinstall_repo(
    repo_name: str,
    ptu: PyprojectTomlUpdater,
    repo_logger: Logger,
    *,
    current_try: int,
) -> CompletedProcess[str]:
    repo_logger.info(f"Building {repo_name}... ({current_try + 1}/{BUILD_TRIES})")

    result = run_subprocess_shell(
        f"export PATH={PDM_BIN_DIR} \
                && cd {REPOS_DIR}/{repo_name} \
                && pdm sync --reinstall \
            ",
        repo_logger,
        timeout=60 * 10,
    )
    if result.stdout:
        repo_logger.info(result.stdout)
    if result.stderr:
        repo_logger.warning(result.stderr)
    if result.returncode != 0:
        repo_logger.error(
            f"Failed to build {repo_name} ({current_try + 1}/{BUILD_TRIES})"
        )

    return result


def pip_build_repo(
    repo_name: str,
    ptu: PyprojectTomlUpdater,
    repo_logger: Logger,
    *,
    use_orig_pyproject_toml: bool,
) -> CompletedProcess[str]:
    repo_logger.info(f"Building {repo_name} using `pip install -e .`...")

    if use_orig_pyproject_toml:
        ptu.revert_to_orig()
        repo_logger.info(f"Reverted pyproject.toml for {repo_name}")

    if os.path.exists(f"{REPOS_DIR}/{repo_name}/.venv"):
        result = run_subprocess_shell(
            f"""export PATH={PDM_BIN_DIR} \
                && cd {REPOS_DIR}/{repo_name} ;
                cat pipreqs_r2e_requirements.txt | xargs -n 1 .venv/bin/python -m pip install ;
                for file in requirements*.txt; do
                    cat $file | xargs -n 1 .venv/bin/python -m pip install ;
                done
                for file in requirements/*.txt; do
                    cat $file | xargs -n 1 .venv/bin/python -m pip install ;
                done
                .venv/bin/python -m pip install -e . ;
            """,
            repo_logger,
            timeout=60 * 5,
        )
    else:
        result = run_subprocess_shell(
            f"""export PATH={PDM_BIN_DIR} \
                && cd {REPOS_DIR}/{repo_name} ;
                pdm venv create 3.11 ; 
                cat pipreqs_r2e_requirements.txt | xargs -n 1 .venv/bin/python -m pip install ;
                for file in requirements*.txt; do
                    cat $file | xargs -n 1 .venv/bin/python -m pip install ;
                done
                for file in requirements/*.txt; do
                    cat $file | xargs -n 1 .venv/bin/python -m pip install ;
                done
                .venv/bin/python -m pip install -e . ;
            """,
            repo_logger,
            timeout=60 * 5,
        )

    if result.stdout:
        repo_logger.info(result.stdout)
    if result.stderr:
        repo_logger.warning(result.stderr)
    if result.returncode != 0:
        repo_logger.error(f"Failed to build {repo_name} using `pip install -e .`")

    return result
