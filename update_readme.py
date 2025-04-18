import os
import requests
import subprocess
import json
import shutil
import platform

GITHUB_USERNAME = "RafalSa"
GITHUB_API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

def get_repos():
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repositories: {response.status_code}")
        return []

def count_lines_in_repo(repo_url, repo_name):
    try:
        if os.path.exists(repo_name):
            shutil.rmtree(repo_name)

        subprocess.run(['git', 'clone', '--depth', '1', repo_url, repo_name], check=True)

        result = subprocess.run(['cloc', repo_name, '--json'], capture_output=True, text=True)
        data = json.loads(result.stdout)

        return data.get('SUM', {}).get('code', 0)
    except Exception as e:
        print(f"Error counting lines for {repo_name}: {e}")
        return 0
    finally:
        if os.path.exists(repo_name):
            shutil.rmtree(repo_name)

readme_path = "README.md"

with open(readme_path, "r", encoding="utf-8") as readme_file:
    readme_content = readme_file.readlines()

start_marker = "<!--START_SECTION:code_line_count-->\n"
end_marker = "<!--END_SECTION:code_line_count-->\n"

if start_marker not in readme_content:
    readme_content.insert(0, start_marker)
if end_marker not in readme_content:
    readme_content.append(end_marker)

start_index = readme_content.index(start_marker) + 1
end_index = readme_content.index(end_marker)

repos = get_repos()

repo_line_counts = []
for repo in repos:
    repo_name = repo['name']
    repo_url = repo['html_url']
    lines_of_code = count_lines_in_repo(repo['clone_url'], repo_name)
    repo_line_counts.append((repo_name, repo_url, lines_of_code))

# Sortuj i wybierz TOP 10
repo_line_counts.sort(key=lambda x: x[2], reverse=True)
top_repos = repo_line_counts[:10]

new_section = [f"- **[{name}]({url})**: {lines} lines of code\n" for name, url, lines in top_repos]

# Zastąp tylko sekcję pomiędzy znacznikami
readme_content[start_index:end_index] = new_section

with open(readme_path, "w", encoding="utf-8") as readme_file:
    readme_file.writelines(readme_content)

print("README.md zostało zaktualizowane z top 10 repozytoriami!")
