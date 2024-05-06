import re
from logging import Logger

from paths import REPOS_DIR, PDM_BIN_DIR
from pdm_import_utils import pdm_import_all
from bash_utils import run_subprocess_shell
from toml_updator import PyprojectTomlUpdater


def init_pdm(repo_name: str, repo_logger: Logger):
    result = run_subprocess_shell(
        f"export PATH={PDM_BIN_DIR} \
            && cd {REPOS_DIR}/{repo_name} \
            && pdm init --non-interactive \
        ",
        repo_logger,
    )
    if result.stdout:
        repo_logger.info(result.stdout)
    if result.stderr:
        repo_logger.warning(result.stderr)
    return result


def repair_pyproject_toml(
    repo_name,
    ptu: PyprojectTomlUpdater,
    stdout,
    stderr,
    returncode,
    repo_logger: Logger,
):
    repo_logger.info(f"Repairing build for {repo_name}...")
    if (
        "pdm.backend.exceptions.ValidationError: "
        'Field "project.version" missing and '
        '"version" not specified in "project.dynamic"' in stderr
    ):
        ptu.update(("project", "version"), "0.1.0", "project.version_missing")
        repo_logger.info(f"Added project.version as '0.1.0' for {repo_name}")

    REQUIRES_PYTHON_ERROR = (
        r"A possible solution is to change the value of "
        "`requires-python` in pyproject.toml to (.+).\n"
    )
    m = re.search(REQUIRES_PYTHON_ERROR, stderr)
    if m:
        requires_python = m.group(1)
        ptu.update(
            ("project", "requires-python"), requires_python, "project.requires-python"
        )
        repo_logger.info(
            f"Added project.requires-python as '{requires_python}' for {repo_name}"
        )

    if (
        "[ProjectError]: The pyproject.toml has not been initialized yet. "
        "You can do this by running `pdm init`." in stderr
    ):
        repo_logger.info(f"Initializing pyproject.toml for {repo_name}")
        result = init_pdm(repo_name, repo_logger)
        if result.returncode != 0:
            repo_logger.error(f"Failed to initialize pyproject.toml for {repo_name}")
        ptu.update(
            ("project", "authors"),
            [{"name": "FirstName LastName", "email": "123@456.com"}],  # type: ignore
            "project.authors",
        )
        pdm_import_all(repo_name, ptu, repo_logger)

    if "pdm.formats.base.MetaConvertError: \ndependencies: 'dependencies'" in stderr:
        ptu.update(None, None, "pdm.formats...dependencies", write_data={})
        repo_logger.info(f"Cleared pyproject.toml for {repo_name}")

        result = init_pdm(repo_name, repo_logger)
        if result.returncode != 0:
            repo_logger.error(
                f"Failed to repair pdm.formats...dependencies for {repo_name}"
            )
        pdm_import_all(repo_name, ptu, repo_logger)
