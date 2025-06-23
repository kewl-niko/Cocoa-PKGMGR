import subprocess
import sys
import re
from colorama import Fore, Style, init

init(autoreset=True)


def run_subprocess(command):
    subprocess.run(command)


def show_help():
    print(Style.DIM + """
Cocoa - Win-Get made easy.
Made with love by niko!!

Usage:
  -R {query}    Removes an app from the installed list.
  -S {query}    Searches for an app and installs the one selected.
  -AAU          Updates all installed MS-Store apps.
  --help, -H    Show this message.
""".strip())


def search_and_install(query):
    print(Fore.YELLOW + "Searching for app... Press Ctrl+C to cancel.\n")
    try:
        result = subprocess.run(["winget", "search", query], capture_output=True, text=True)
        lines = result.stdout.splitlines()

        # Skip lines before headers
        app_lines = []
        header_found = False
        for line in lines:
            if "Name" in line and "Id" in line:
                header_found = True
                continue
            if header_found and line.strip() and not line.startswith("-"):
                app_lines.append(line.strip())

        parsed_apps = []
        for line in app_lines:
            match = re.match(r'^(.+?)\s{2,}([^\s]+)', line)
            if match:
                name = match.group(1).strip()
                app_id = match.group(2).strip()
                parsed_apps.append((name, app_id))

        if not parsed_apps:
            print(Fore.RED + "No apps found.")
            return

        for i, (name, app_id) in enumerate(parsed_apps, 1):
            print(f"{Fore.CYAN}[{i}]{Style.RESET_ALL} {Fore.WHITE}{name}{Style.DIM} - {app_id}")

        choice = input(Fore.YELLOW + "\nPick a number from above (or Ctrl+C to cancel): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(parsed_apps)):
            print(Fore.RED + "Invalid choice. Aborting.")
            return

        _, chosen_id = parsed_apps[int(choice) - 1]

        print(Fore.GREEN + f"\nInstalling: {chosen_id}")
        run_subprocess(["winget", "install", "--id", chosen_id, "-e", "--accept-package-agreements", "--accept-source-agreements"])

    except KeyboardInterrupt:
        print(Fore.RED + "\nInstallation cancelled.")


def remove_app(query):
    print(Fore.CYAN + "Searching for installed app..." + Style.RESET_ALL)

    try:
        result = subprocess.run(
            ["winget", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",  # <- This fixes UnicodeDecodeError
            errors="ignore"    # <- Silently skip bad chars
        )
    except Exception as e:
        print(Fore.RED + f"Failed to list apps: {e}" + Style.RESET_ALL)
        return

    lines = result.stdout.splitlines()

    matches = []
    for line in lines:
        if query.lower() in line.lower():
            matches.append(line.strip())

    if not matches:
        print(Fore.RED + "No matching apps found." + Style.RESET_ALL)
        return

    # Display list
    for idx, item in enumerate(matches, 1):
        parts = item.split()
        name = parts[0]
        app_id = parts[1] if len(parts) > 1 else ""
        print(Fore.LIGHTBLACK_EX + f"[{idx}] {name} - {app_id}" + Style.RESET_ALL)

    try:
        choice = int(input(Fore.YELLOW + "\nPick a number to remove (or Ctrl+C to cancel): " + Style.RESET_ALL))
        selected = matches[choice - 1]
        parts = selected.split()
        app_name = parts[0]
        app_id = parts[1] if len(parts) > 1 else ""

        full_name = f"{app_name} {app_id}".strip()
        confirm = input(Fore.RED + f"Are you sure you want to remove '{full_name}'? (y/N): " + Style.RESET_ALL)

        if confirm.lower() == "y":
            print(Fore.CYAN + f"Uninstalling: {full_name}" + Style.RESET_ALL)
            uninstall = subprocess.run(["winget", "uninstall", "--id", app_id, "--accept-source-agreements"])
            if uninstall.returncode != 0:
                subprocess.run(["winget", "uninstall", "--name", app_name, "--accept-source-agreements"])
        else:
            print(Fore.YELLOW + "Canceled." + Style.RESET_ALL)

    except (ValueError, IndexError):
        print(Fore.RED + "Invalid choice." + Style.RESET_ALL)
    except KeyboardInterrupt:
        print(Fore.RED + "\nCancelled." + Style.RESET_ALL)

def update_all_apps():
    confirm = input(Fore.YELLOW + "Are you sure you want to update ALL MS Store apps? (y/N): ").lower()
    if confirm != 'y':
        print(Fore.RED + "Update cancelled.")
        return

    print(Fore.GREEN + "Updating all apps...")
    run_subprocess(["winget", "upgrade", "--all", "--accept-package-agreements", "--accept-source-agreements"])


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-H"]:
        show_help()
    elif sys.argv[1] == "-S" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        search_and_install(query)
    elif sys.argv[1] == "-R" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        remove_app(query)
    elif sys.argv[1] == "-AAU":
        update_all_apps()
    else:
        show_help()


if __name__ == "__main__":
    main()
