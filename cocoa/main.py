import subprocess
import sys

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def search_packages(term):
    print(f"Searching for packages with term: {term}")
    cmd = f"winget search {term}"
    out, err, code = run_command(cmd)
    if code == 0:
        print(out)
    else:
        print(f"Error searching packages: {err}")

def remove_package(name_or_id):
    print(f"Removing package: {name_or_id}")
    cmd = f"winget uninstall --id {name_or_id} --accept-package-agreements --accept-source-agreements"
    out, err, code = run_command(cmd)
    if code == 0:
        print(out)
    else:
        # Try by name if uninstall by ID fails
        print(f"Failed to uninstall by ID, trying by name...")
        cmd = f"winget uninstall --name \"{name_or_id}\" --accept-package-agreements --accept-source-agreements"
        out, err, code = run_command(cmd)
        if code == 0:
            print(out)
        else:
            print(f"Failed to uninstall package: {err}")

def all_apps_upgrade():
    print("Upgrading all installed packages from the Microsoft Store...")
    print("Just sit back and relax, It's gonna take a while.")
    # List all installed packages
    list_cmd = "winget list"
    out, err, code = run_command(list_cmd)
    if code != 0:
        print(f"Failed to list packages: {err}")
        return
    
    # Parse output, get package IDs or Names
    lines = out.splitlines()
    # The output header usually has columns: Name, Id, Version, Available, Source
    # We'll try to parse lines and collect apps from 'msstore' source
    packages_to_upgrade = []
    for line in lines[2:]:  # skip header lines
        parts = line.split()
        if len(parts) < 5:
            continue
        # Try to parse source as last column
        source = parts[-1]
        if source.lower() == "msstore":
            # Package Id or Name might be in first or second columns
            # We'll pick the ID (2nd column)
            package_id = parts[1]
            packages_to_upgrade.append(package_id)
    
    if not packages_to_upgrade:
        print("No Microsoft Store apps found to upgrade.")
        return
    
    print(f"Found {len(packages_to_upgrade)} Microsoft Store apps to upgrade...")
    for pkg in packages_to_upgrade:
        print(f"Upgrading {pkg}...")
        cmd = f"winget upgrade --id {pkg} --accept-package-agreements --accept-source-agreements"
        out, err, code = run_command(cmd)
        if code == 0:
            print(f"Successfully upgraded {pkg}")
        else:
            print(f"Failed to upgrade {pkg}: {err}")

def print_help():
    print("""
    Cocoa is a wrapper for Win-Get to make it quite easier to use.
    Made with love, by niko.

Usage:
    -S <search_term>    Search for packages matching the term
    -R <package_name_or_id>    Remove/uninstall a package by name or ID
    -AAU                Upgrade all installed Microsoft Store apps
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    arg = sys.argv[1].upper()
    
    if arg == "-S" and len(sys.argv) >= 3:
        search_packages(sys.argv[2])
    elif arg == "-R" and len(sys.argv) >= 3:
        remove_package(sys.argv[2])
    elif arg == "-AAU":
        all_apps_upgrade()
    elif arg == "-H" or arg == "--help":
        print_help()
    else:
        print_help()

if __name__ == "__main__":
    main()
