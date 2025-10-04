import os
import requests
import subprocess
import json
import shutil
import platform

GITHUB_USERNAME = "RafalSa"
GITHUB_API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

def get_repos():
    repos = []
    page = 1
    per_page = 100  # maksymalna wartość dla GitHub API

    while True:
        url = f"{GITHUB_API_URL}?per_page={per_page}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}")
            break
        page_data = response.json()
        if not page_data:
            break
        repos.extend(page_data)
        page += 1

    return repos

def count_lines_in_repo(repo_url, repo_name):
    try:
        if os.path.exists(repo_name):
            shutil.rmtree(repo_name)
        subprocess.run(['git', 'clone', repo_url, repo_name], check=True)
        result = subprocess.run(['cloc', repo_name, '--json'], capture_output=True, text=True)
        data = json.loads(result.stdout)
        return data['SUM']['code']
    except Exception as e:
        print(f"Error counting lines for {repo_name}: {e}")
        return 0

def update_readme():
    readme_path = "README.md"

    if not os.path.exists(readme_path):
        print("README.md not found!")
        return

    with open(readme_path, "r") as file:
        content = file.readlines()

    start_marker = "<!--START_SECTION:code_line_count-->\n"
    end_marker = "<!--END_SECTION:code_line_count-->\n"

    if start_marker not in content:
        content.insert(0, start_marker)
    if end_marker not in content:
        content.insert(content.index(start_marker) + 1, end_marker)

    start_index = content.index(start_marker) + 1
    end_index = content.index(end_marker)

    repos = get_repos()
    repo_lines = []

    print("Liczenie linii kodu...")

    for repo in repos:
        repo_name = repo['name']
        repo_url = repo['clone_url']
        lines = count_lines_in_repo(repo_url, repo_name)
        repo_lines.append((repo_name, repo['html_url'], lines))

    # Sortowanie i wybranie 10 największych
    repo_lines.sort(key=lambda x: x[2], reverse=True)
    top_10 = repo_lines[:10]

    new_section = [
        f"- **[{name}]({url})**: {lines} lines of code\n"
        for name, url, lines in top_10
    ]

    # Wstawienie nowej sekcji do README
    content[start_index:end_index] = new_section

    with open(readme_path, "w") as file:
        file.writelines(content)

    print("README.md zostało zaktualizowane!")

if __name__ == "__main__":
    update_readme()
