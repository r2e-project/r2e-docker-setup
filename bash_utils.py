import subprocess
from logging import Logger
from subprocess import CompletedProcess


def run_subprocess_shell(
    command: str, repo_logger: Logger | None = None, **kwargs
) -> CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            executable="/bin/bash",
            shell=True,
            capture_output=True,
            text=True,
            # check=True,
            **kwargs,
        )
    except subprocess.TimeoutExpired as e:
        if repo_logger:
            repo_logger.error(f"Timeout expired for {command}")
        result = CompletedProcess(
            args=command,
            returncode=1,
            stderr="Timeout expired",
        )
    except subprocess.CalledProcessError as e:
        if repo_logger:
            repo_logger.error(f"CalledProcessError running {command} -- {e}")
        result = CompletedProcess(
            args=command,
            returncode=1,
        )
    except Exception as e:
        if repo_logger:
            repo_logger.error(f"Error running {command} -- {e}")
        result = CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr=str(e),
        )
    return result
