import logging
from pathlib import Path

from paths import REPOS_DIR
from logger import setup_logging
from bash_utils import run_subprocess_shell
from pdm_import_utils import pdm_import_all
from repair_toml import repair_pyproject_toml
from toml_updator import PyprojectTomlUpdater
from pdm_pip_install import pdm_build_repo, pip_build_repo, pdm_reinstall_repo

BUILD_TRIES = 3


def install_single_repo(repo_name: str):
    repo_logger = setup_logging(
        name=repo_name,
        log_file=f"install_logs/{repo_name}.log",
        console=False,
        level=logging.INFO,
    )
    ptu = PyprojectTomlUpdater(Path(f"{REPOS_DIR}/{repo_name}/pyproject.toml"))

    pdm_import_all(repo_name, ptu, repo_logger)

    use_orig_pyproject_toml = False  # not used
    for i in range(BUILD_TRIES):
        result = pdm_build_repo(repo_name, ptu, repo_logger, current_try=i)
        if result.returncode == 0:
            result = pdm_reinstall_repo(repo_name, ptu, repo_logger, current_try=i)
            if result.returncode == 0:
                break

        if (
            "[ResolutionImpossible]: Unable to find a resolution" in result.stderr
            and "A possible solution is to change the value of " not in result.stderr
        ):
            repo_logger.info(
                f"Skipping {repo_name} build due to "
                "[ResolutionImpossible]: Unable to find a resolution"
            )
            break

        repair_pyproject_toml(
            repo_name,
            ptu,
            result.stdout,
            result.stderr,
            result.returncode,
            repo_logger,
        )
    else:
        use_orig_pyproject_toml = True
        repo_logger.error(f"Failed to build {repo_name} using pdm")

    pip_build_repo(
        repo_name,
        ptu,
        repo_logger,
        use_orig_pyproject_toml=True,
    )

    run_subprocess_shell(
        f"cd {REPOS_DIR}/{repo_name} && .venv/bin/python -m pip install r2e_test_server",
        repo_logger,
    )
