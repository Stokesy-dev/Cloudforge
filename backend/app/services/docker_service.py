import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    output: str
    value: str | None = None


def _run(args: list[str], cwd: str | None = None) -> CommandResult:
    try:
        process = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=900, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CommandResult(False, str(exc))
    output = (process.stdout + "\n" + process.stderr).strip()
    return CommandResult(process.returncode == 0, output)


def docker_available() -> bool:
    return _run(["docker", "info"]).ok


def build_image(context: str, image: str) -> CommandResult:
    return _run(["docker", "build", "--tag", image, context], cwd=context)


def start_container(image: str, name: str, port: int = 8000) -> CommandResult:
    result = _run(["docker", "run", "--detach", "--name", name, "--publish", f"{port}:{port}", image])
    return CommandResult(result.ok, result.output, result.output.splitlines()[-1][:128] if result.ok and result.output else None)


def stop_container(name: str) -> CommandResult:
    return _run(["docker", "rm", "--force", name])


def container_logs(name: str) -> CommandResult:
    return _run(["docker", "logs", "--tail", "500", name])
