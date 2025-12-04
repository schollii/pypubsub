#!/usr/bin/env python3
"""Release helper for tag-based publishing.

Subcommands:
  - get-latest: print latest vX.Y.Z tag (defaults to v0.0.0 if none)
  - bump-local {major,minor,patch}: ensure clean tree, compute next version from latest tag, create local tag
  - init-tag <vX.Y.Z>: create the first tag if none exists (no bump)
  - push-tag [tag]: warn and push the given tag (defaults to latest)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Tuple


def run(cmd: list[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        capture_output=capture_output,
    )


def require_clean_worktree() -> None:
    status = run(["git", "status", "--porcelain"])
    if status.stdout.strip():
        print("Working tree is not clean. Commit or stash changes first.", file=sys.stderr)
        sys.exit(1)


def latest_tag() -> str:
    res = run(["git", "describe", "--tags", "--abbrev=0"])
    if res.returncode != 0:
        return "v0.0.0"
    return res.stdout.strip()


def parse_version(tag: str) -> Tuple[int, int, int]:
    if not tag.startswith("v"):
        raise ValueError(f"Tag '{tag}' does not start with 'v'")
    try:
        major, minor, patch = (int(part) for part in tag[1:].split("."))
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unable to parse tag '{tag}'") from exc
    return major, minor, patch


def format_tag(version: Tuple[int, int, int]) -> str:
    return f"v{version[0]}.{version[1]}.{version[2]}"


def bump_version(tag: str, bump: str) -> str:
    major, minor, patch = parse_version(tag)
    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "patch":
        patch += 1
    else:  # pragma: no cover - argparse enforces choices
        raise ValueError(f"Unknown bump type: {bump}")
    return format_tag((major, minor, patch))


def tag_exists(tag: str) -> bool:
    return run(["git", "rev-parse", tag]).returncode == 0


def cmd_get_latest(_: argparse.Namespace) -> None:
    print(latest_tag())


def cmd_bump_local(args: argparse.Namespace) -> None:
    require_clean_worktree()
    current = latest_tag()
    if current == "v0.0.0":
        print("No existing tag found. Use init-tag first.", file=sys.stderr)
        sys.exit(1)
    new_tag = bump_version(current, args.bump)
    if tag_exists(new_tag):
        print(f"Tag {new_tag} already exists.", file=sys.stderr)
        sys.exit(1)
    print(f"Current tag: {current}")
    print(f"New tag:     {new_tag}")
    confirm = input("Create local tag? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(1)
    res = run(["git", "tag", new_tag], capture_output=False)
    if res.returncode != 0:
        print("Failed to create tag", file=sys.stderr)
        sys.exit(res.returncode)
    print(f"Tag created: {new_tag}")


def cmd_push_tag(args: argparse.Namespace) -> None:
    tag = args.tag or latest_tag()
    if not tag_exists(tag):
        print(f"Tag {tag} does not exist.", file=sys.stderr)
        sys.exit(1)
    print(f"About to push {tag} to origin.")
    print("Warning: pushing a v* tag triggers the GitHub Actions release workflow, which uploads to PyPI.")
    confirm = input("Push now? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(1)
    res = run(["git", "push", "origin", tag], capture_output=False)
    sys.exit(res.returncode)


def cmd_init_tag(args: argparse.Namespace) -> None:
    require_clean_worktree()
    if latest_tag() != "v0.0.0":
        print("A tag already exists; use bump-local instead.", file=sys.stderr)
        sys.exit(1)
    tag = args.tag
    if not tag.startswith("v"):
        print("Tag must start with 'v', e.g. v4.0.4", file=sys.stderr)
        sys.exit(1)
    try:
        parse_version(tag)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(f"About to create initial tag {tag}.")
    print("Warning: pushing this tag will trigger the release workflow to PyPI.")
    confirm = input("Create tag locally? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(1)
    res = run(["git", "tag", tag], capture_output=False)
    if res.returncode != 0:
        print("Failed to create tag", file=sys.stderr)
        sys.exit(res.returncode)
    print(f"Tag created: {tag}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Release helper for tag-based publishing.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("get-latest", help="Print latest vX.Y.Z tag").set_defaults(func=cmd_get_latest)

    bump = sub.add_parser("bump-local", help="Bump from latest tag and create a local tag")
    bump.add_argument("bump", choices=["major", "minor", "patch"], help="Version segment to bump")
    bump.set_defaults(func=cmd_bump_local)

    initp = sub.add_parser("init-tag", help="Create an initial tag when none exists")
    initp.add_argument("tag", help="Initial tag (format vX.Y.Z)")
    initp.set_defaults(func=cmd_init_tag)

    push = sub.add_parser("push-tag", help="Push an existing tag to origin (triggers release workflow)")
    push.add_argument("tag", nargs="?", help="Tag to push (defaults to latest)")
    push.set_defaults(func=cmd_push_tag)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
