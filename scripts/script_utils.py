import os
import re
import subprocess
from enum import Enum
from typing import List

class Config:
    PARENT_BRANCH = "dev"
    EXCLUDE_SRC_FOLDERS = [
        "repos/starkware-public/build",
        "build",
        "bazel-out",
        "src/services/starkex/docs",
        ".*/node_modules",
        r".*\.tox",
        "src/third_party",
        ".*/third_party",
    ]


class Color(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    LIGHT_GRAY = 37
    DEFAULT = 39
    DARK_GRAY = 90
    LIGHT_RED = 91
    LIGHT_GREEN = 92
    LIGHT_YELLOW = 93
    LIGHT_BLUE = 94
    LIGHT_MAGENTA = 95
    LIGHT_CYAN = 96
    WHITE = 97


def exec_command(command: str, cwd=None):
    try:
        return subprocess.check_output(command, shell=True, cwd=cwd).decode("utf-8").splitlines()
    except subprocess.CalledProcessError:
        print(f"Error executing command: {command}")
        raise


def get_parent_branch(file_location: str):
    try:
        with open(file_location, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"parent_branch.txt file not found at location: {file_location}")
        raise


def create_grep_pipe_command(extensions) -> str:
    if extensions is None:
        return ''
    return r' | { grep -E "\.(%s)$" || true; }' % ('|'.join(extensions))


def git_files(extensions=None) -> List[str]:
    return get_files("git ls-tree -r --name-only HEAD", extensions)


def changed_files(extensions=None, include_excluded_files=False) -> List[str]:
    return get_files(f"git diff --name-only $(git merge-base origin/{Config.PARENT_BRANCH} HEAD)", extensions=extensions, include_excluded_files=include_excluded_files)


def get_files(git_cmd: str, extensions=None, include_excluded_files=False, cwd=None) -> List[str]:
    if cwd is None:
        cwd = os.getcwd()

    command = f"{git_cmd} {create_grep_pipe_command(extensions)}"  # All git files
    files: List[str] = exec_command(command, cwd=cwd)

    # Filter out exclusion list.
    if not include_excluded_files:
        exclude_pattern = f'^({"|".join(Config.EXCLUDE_SRC_FOLDERS)})'
        files = [f for f in files if not re.match(exclude_pattern, f)]

    # Filter to include only real files.
    files = [f for f in files if os.path.isfile(os.path.join(cwd, f))]

    return files


def find_command(command_name: str) -> str:
    try:
        return exec_command(["which", command_name])[0]
    except subprocess.CalledProcessError:
        print(f"{command_name} not installed.")
        raise
