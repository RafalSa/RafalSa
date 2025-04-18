import os
import requests
import subprocess
import json
import shutil
import platform

# GitHub API endpoint do pobierania repozytoriów użytkownika
GITHUB_USERNAME = "RafalSa"  # Zastąp swoją nazwą użytkownika
GITHUB_API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

# Funkcja do pobierania listy repozytoriów
def get_repos():
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repositories: {response.status_code}")
        return []

# Funkcja do zliczania linii kodu w danym repozytorium
def count_lines_in_repo(repo_url, repo_name):
    try:
        # Usunięcie istniejącego folderu, jeśli już istnieje
        if os.path.exists(repo_name):
            if platform.system() == "Windows":
                subprocess.run(['rmdir', '/S', '/Q', repo_name], check=True)  # Działa w Windows
            else:
                shutil.rmtree(repo_name)  # Działa w Linux/Mac

        # Klonowanie repozytorium do lokalnego katalogu tymczasowego
        subprocess.run(['git', 'clone', repo_url, repo_name], check=True)

        # Zliczanie linii kodu za pomocą cloc
        result = subprocess.run(['cloc', repo_name, '--json'], capture_output=True, text=True)
        data = json.loads(result.stdout)

        return data['SUM']['code']
    except Exception as e:
        print(f"Error counting lines for {repo_name}: {e}")
        return 0

# Ścieżka do pliku README.md
readme_path = "README.md"

# Pobieranie istniejącego pliku README.md
with open(readme_path, "r") as readme_file:
    readme_content = readme_file.readlines()

# Markery, gdzie chcemy dodać zestawienie linii kodu
start_marker = "<!--START_SECTION:code_line_count-->\n"
end_marker = "<!--END_SECTION:code_line_count-->\n"

# Dodanie markerów, jeśli ich brak
if start_marker not in readme_content:
    readme_content.insert(0, start_marker)
if end_marker not in readme_content:
    readme_content.append(end_marker)

# Zlokalizowanie pozycji markerów
start_index = readme_content.index(start_marker) + 1
end_index = readme_content.index(end_marker)

# Pobieranie wszystkich repozytoriów
repos = get_repos()

# Lista repozytoriów z liczbą linii kodu
repos_with_lines = []

# Generowanie zestawienia z repozytoriami
for repo in repos:
    repo_name = repo['name']
    repo_url = repo['html_url']
    lines_of_code = count_lines_in_repo(repo_url, repo_name)
    repos_with_lines.append((repo_name, repo_url, lines_of_code))

# Sortowanie repozytoriów po liczbie linii kodu, w porządku malejącym
repos_with_lines.sort(key=lambda x: x[2], reverse=True)

# Wybieranie tylko 10 repozytoriów z największą liczbą linii kodu
top_10_repos = repos_with_lines[:10]

# Generowanie nowego zestawienia dla README
new_content = []
for repo_name, repo_url, lines_of_code in top_10_repos:
    new_content.append(f"- **[{repo_name}]({repo_url})**: {lines_of_code} lines of code\n")

# Aktualizacja zawartości README.md
readme_content[start_index:end_index] = new_content

# Zapisanie zaktualizowanego pliku README.md
with open(readme_path, "w") as readme_file:
    readme_file.writelines(readme_content)

print("README.md zostało zaktualizowane!")
