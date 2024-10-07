import os
import subprocess

# Funkcja do zliczania linii kodu w repozytorium za pomocą cloc
def count_lines_in_repo(repo_path):
    try:
        # Uruchomienie cloc i wyciągnięcie wyniku
        result = subprocess.run(['cloc', repo_path, '--json'], capture_output=True, text=True)
        # Pobranie danych z wyniku (JSON)
        data = eval(result.stdout)
        return data['SUM']['code']  # Zwraca liczbę linii kodu
    except Exception as e:
        print(f"Error counting lines in {repo_path}: {e}")
        return 0

# Lista repozytoriów do analizy (podaj tutaj swoje repozytoria)
repos = ['repo1', 'repo2', 'repo3']

# Ścieżka do pliku README.md
readme_path = "README.md"

# Odczytanie istniejącego pliku README.md
with open(readme_path, "r") as readme_file:
    readme_content = readme_file.readlines()

# Szukaj miejsca w pliku README.md, gdzie chcemy dodać zestawienie
start_marker = "<!--START_SECTION:code_line_count-->\n"
end_marker = "<!--END_SECTION:code_line_count-->\n"

start_index = readme_content.index(start_marker) + 1
end_index = readme_content.index(end_marker)

# Generowanie nowych danych do umieszczenia w README.md
new_content = [f"- **{repo}**: {count_lines_in_repo(repo)} linijek kodu\n" for repo in repos]

# Zaktualizuj treść README.md
readme_content[start_index:end_index] = new_content

# Zapisanie pliku README.md
with open(readme_path, "w") as readme_file:
    readme_file.writelines(readme_content)

print("README.md zostało zaktualizowane!")
