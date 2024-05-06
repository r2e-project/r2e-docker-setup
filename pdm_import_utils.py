import os
from pathlib import Path
from logging import Logger

from paths import REPOS_DIR, PDM_BIN_DIR
from bash_utils import run_subprocess_shell
from toml_updator import PyprojectTomlUpdater


def pdm_import(
    repo_name: str,
    ptu: PyprojectTomlUpdater,
    file_name: str,
    format: str,
    repo_logger: Logger,
):
    if not Path(f"{REPOS_DIR}/{repo_name}/{file_name}").exists():
        return

    ptu.update(None, None, f"pdm_import_{file_name}_{format}")
    repo_logger.info(f"Importing {file_name} for {repo_name}...")

    result = run_subprocess_shell(
        f"""export PATH={PDM_BIN_DIR} 
            cd {REPOS_DIR}/{repo_name}
            if [ -f {file_name} ]; then
                pdm import {file_name} --format {format}
            fi
        """,
        repo_logger,
    )
    if result.stdout:
        repo_logger.info(result.stdout)
    if result.stderr:
        repo_logger.warn(result.stderr)
    if result.returncode != 0:
        if format == "poetry" and "[KeyError]: 'tool'" in result.stderr:
            return
        if format == "poetry" and "[KeyError]: 'poetry'" in result.stderr:
            return
        if format == "flit" and "[KeyError]: 'tool'" in result.stderr:
            return
        if format == "flit" and "[KeyError]: 'flit'" in result.stderr:
            return
        repo_logger.error(f"Failed to import {file_name} as {format} for {repo_name}")


def create_pipreqs_file(repo_name: str, repo_logger: Logger):
    repo_logger.info(f"Creating requirements.txt for {repo_name}...")

    result = run_subprocess_shell(
        f"""cd {REPOS_DIR}/{repo_name}
            source ~/.bashrc
            pipreqs --encoding=iso-8859-1 --ignore .venv --savepath pipreqs_r2e_requirements.txt --mode no-pin .
        """,
        repo_logger,
    )
    if result.stdout:
        repo_logger.info(result.stdout)
    if result.stderr:
        if "pipreqs: command not found" in result.stderr:
            raise Exception("pipreqs not found")
            return
        repo_logger.warn(result.stderr)
    if result.returncode != 0:
        repo_logger.error(
            f"Failed to create pipreqs_r2e_requirements.txt for {repo_name}"
        )


def pdm_import_all(
    repo_name: str,
    ptu: PyprojectTomlUpdater,
    repo_logger: Logger,
):

    create_pipreqs_file(repo_name, repo_logger)
    pdm_import(
        repo_name,
        ptu,
        "pipreqs_r2e_requirements.txt",
        "requirements",
        repo_logger,
    )
    pdm_import(repo_name, ptu, "pyproject.toml", "poetry", repo_logger)
    pdm_import(repo_name, ptu, "pyproject.toml", "flit", repo_logger)

    try:
        all_files = os.listdir(f"{REPOS_DIR}/{repo_name}")
        for file_name in all_files:
            if file_name == "pipreqs_r2e_requirements.txt":
                continue
            if file_name.startswith("requirements") and file_name.endswith(".txt"):
                pdm_import(repo_name, ptu, file_name, "requirements", repo_logger)
    except Exception as e:
        repo_logger.error(f"Failed to import requirements files for {repo_name}")

    try:
        all_files = os.listdir(f"{REPOS_DIR}/{repo_name}/requirements")
        for file_name in all_files:
            if file_name.endswith(".txt"):
                pdm_import(repo_name, ptu, file_name, "requirements", repo_logger)
    except Exception as e:
        repo_logger.error(f"Failed to import requirements files for {repo_name}")

    pdm_import(repo_name, ptu, "requirements.in", "requirements", repo_logger)
    pdm_import(repo_name, ptu, "Pipfile", "pipfile", repo_logger)
    pdm_import(repo_name, ptu, "setup.py", "setuppy", repo_logger)
    pdm_import(repo_name, ptu, "setup.cfg", "setuppy", repo_logger)
