import argparse
from pathlib import Path
from .manager import PromptManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Prompt Manager CLI")
    parser.add_argument("root", help="Root directory for prompts")
    subparsers = parser.add_subparsers(dest="cmd")

    subparsers.add_parser("list-projects")

    lp = subparsers.add_parser("list-prompts")
    lp.add_argument("project")

    sv = subparsers.add_parser("show-versions")
    sv.add_argument("project")
    sv.add_argument("prompt")

    exp = subparsers.add_parser("export")
    exp.add_argument("project")
    exp.add_argument("prompt")
    exp.add_argument("file")

    imp = subparsers.add_parser("import")
    imp.add_argument("file")
    imp.add_argument("dest", nargs="?")

    args = parser.parse_args()
    pm = PromptManager(Path(args.root))

    if args.cmd == "list-projects":
        for p in pm.list_projects():
            print(p)
    elif args.cmd == "list-prompts":
        for p in pm.get_project(args.project).list_prompts():
            print(p)
    elif args.cmd == "show-versions":
        pr = pm.get_prompt([args.project, args.prompt])
        for v in pr.versions:
            print(v.version)
    elif args.cmd == "export":
        pr = pm.get_prompt([args.project, args.prompt])
        path = pr.export(args.file)
        print(path)
    elif args.cmd == "import":
        pr = pm.import_prompt(args.file, args.dest)
        print(f"imported {pr.project}/{pr.name}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
