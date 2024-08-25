# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///
import requests
import re
import sys


def fetch_latest_version(package_name):
    url = f"https://test.pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = data["info"]["version"]
        return latest_version
    else:
        print(f"Failed to fetch package info. Status code: {response.status_code}")
        return None


def extract_dev_number(version_str):
    match = re.search(r"\.dev(\d+)$", version_str)
    if match:
        return int(match.group(1))
    else:
        print(f"Failed to extract dev number from version string: {version_str}")
        return None


def main():
    package_name = "strongpods"
    pyproject_path = "pyproject.toml"

    latest_version = fetch_latest_version(package_name)

    if latest_version is None:
        sys.exit(1)

    print(f"Latest version on TestPyPI: {latest_version}")

    # Load current version from pyproject.toml
    with open(pyproject_path, "r") as f:
        # read line starting with "version = "
        content = f.read()

    regex = r"version\s*=\s*\"(\d+\.\d+\.\d+)\""
    re_match = re.search(regex, content)
    if not re_match:
        print("Failed to find current version in pyproject.toml")
        sys.exit(1)

    current_version = re_match.group(1)
    print(f"Current version in pyproject.toml: {current_version}")

    if latest_version.startswith(current_version):
        # we increment the dev last number
        latest_dev_number = extract_dev_number(latest_version)

        if latest_dev_number is None:
            sys.exit(1)

        new_version = f"{current_version}.dev{latest_dev_number + 1}"
    else:
        # we start a new dev version
        new_version = f"{current_version}.dev0"

    # Update pyproject.toml
    content = re.sub(regex, f'version = "{new_version}"', content)
    with open(pyproject_path, "w") as f:
        f.write(content)

    print(f"New version: {new_version}")


if __name__ == "__main__":
    main()
