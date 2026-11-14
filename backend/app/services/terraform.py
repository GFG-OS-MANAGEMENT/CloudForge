"""Thin wrapper around the Terraform CLI.

Dry-run is the default. In dry-run mode no subprocess is started and no
providers are needed, which keeps the project approachable for beginners.
"""

import json
import shutil
import subprocess
from pathlib import Path

from ..config import Settings


class TerraformError(RuntimeError):
    pass


class TerraformRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def apply(self, resource_id: str, variables: dict[str, object]) -> dict[str, str]:
        if self.settings.dry_run:
            manifest = self._workdir(resource_id) / "generated" / f"{variables['name']}.json"
            return {"mode": "dry-run", "manifest": str(manifest)}

        workdir = self._prepare_workdir(resource_id, variables)
        self._run(workdir, ["init", "-input=false", "-no-color"])
        self._run(workdir, ["apply", "-auto-approve", "-input=false", "-no-color"])
        return self._outputs(workdir)

    def destroy(self, resource_id: str) -> None:
        if self.settings.dry_run:
            return
        workdir = self._workdir(resource_id)
        if not workdir.exists():
            return
        self._run(workdir, ["destroy", "-auto-approve", "-input=false", "-no-color"])

    def _module_dir(self) -> Path:
        if self.settings.terraform_module_dir is not None:
            return self.settings.terraform_module_dir
        repo_root = Path(__file__).resolve().parents[3]
        return repo_root / "infrastructure" / "terraform" / "modules" / "local_demo"

    def _workdir(self, resource_id: str) -> Path:
        return self.settings.workdir / resource_id

    def _prepare_workdir(self, resource_id: str, variables: dict[str, object]) -> Path:
        module_dir = self._module_dir()
        if not module_dir.is_dir():
            raise TerraformError(f"Terraform module not found at {module_dir}")
        workdir = self._workdir(resource_id)
        shutil.copytree(module_dir, workdir, dirs_exist_ok=True)
        (workdir / "terraform.tfvars.json").write_text(json.dumps(variables), encoding="utf-8")
        return workdir

    def _run(self, workdir: Path, args: list[str]) -> str:
        binary = shutil.which(self.settings.terraform_binary)
        if binary is None:
            raise TerraformError(
                f"Terraform binary '{self.settings.terraform_binary}' was not found. "
                "Install Terraform or keep CLOUDFORGE_DRY_RUN=true."
            )
        try:
            result = subprocess.run(
                [binary, *args],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=self.settings.terraform_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TerraformError(
                f"Terraform {args[0]} timed out after "
                f"{self.settings.terraform_timeout_seconds} seconds."
            ) from exc
        if result.returncode != 0:
            output = (result.stderr or result.stdout or "").strip()
            raise TerraformError(f"Terraform {args[0]} failed: {output[-1500:]}")
        return result.stdout

    def _outputs(self, workdir: Path) -> dict[str, str]:
        stdout = self._run(workdir, ["output", "-json", "-no-color"])
        try:
            parsed = json.loads(stdout or "{}")
        except json.JSONDecodeError as exc:
            raise TerraformError("Could not parse Terraform outputs.") from exc
        return {key: str(value.get("value")) for key, value in parsed.items()}
