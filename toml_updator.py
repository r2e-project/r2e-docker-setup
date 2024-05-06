from pathlib import Path
import tomlkit


class PyprojectTomlUpdater:
    def __init__(self, path: Path):
        self.path = path
        self.counter = 0
        self.orig_file_exists = self.path.exists()

        path.touch()

        with open(self.path, "r") as f:
            self.orig_data = tomlkit.load(f)

    def revert_to_orig(self):
        if self.orig_file_exists:
            self.update(None, None, "revert_to_orig", write_data=self.orig_data.copy())
        else:
            self.path.unlink()

    def update(
        self,
        key: str | tuple | None,
        value: str | None,
        reason: str,
        *,
        write_data=None,
    ):
        with open(self.path, "r") as f:
            data = tomlkit.load(f)

        backup_path = (
            self.path.parent
            / f"{self.path.stem}_{self.counter}_pre:{reason}{self.path.suffix}"
        )
        with open(backup_path, "w") as f:
            tomlkit.dump(data, f)

        # Modify the data

        if write_data is not None:
            data = write_data.copy()

        if isinstance(key, str):
            data[key] = value
        elif isinstance(key, tuple) and len(key) == 2:
            data[key[0]][key[1]] = value  # type: ignore

        with open(self.path, "w") as f:
            tomlkit.dump(data, f)

        self.counter += 1
