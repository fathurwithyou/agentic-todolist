import subprocess
import sys


def run_command(command, description):
    print(f"--- {description} ---")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(
            f"Error: {description} failed with exit code {result.returncode}",
            file=sys.stderr,
        )
        sys.exit(result.returncode)

    print(f"--- {description} completed successfully ---")


if __name__ == "__main__":
    run_command("uv run ruff check --fix .", "Running ruff check (with auto-fix)")
    run_command("uv run ruff format .", "Running ruff format")

    print("\nAll Ruff operations finished.")
