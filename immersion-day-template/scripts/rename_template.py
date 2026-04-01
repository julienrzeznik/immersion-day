import sys
import pathlib

def rename_template():
    if len(sys.argv) < 2:
        print("Usage: python rename_template.py <prefix>")
        sys.exit(1)

    prefix = sys.argv[1]
    
    if len(prefix) >= 15:
        print(f"Error: Prefix '{prefix}' must be less than 15 characters (currently {len(prefix)} characters).")
        sys.exit(1)

    search_str = "immersion-day-template"
    # Assuming script is in scripts/
    root_dir = pathlib.Path(__file__).parent.parent.resolve()
    script_path = pathlib.Path(__file__).resolve()
    
    exclude_dirs = {'.git', '.venv', '__pycache__', '.pytest_cache'}
    valid_extensions = {'.py', '.tf', '.tfvars', '.md', '.toml', '.yaml', '.yml'}
    
    modified_files = []

    for path in root_dir.rglob('*'):
        if path.is_dir() and path.name in exclude_dirs:
            continue

        if path.is_file():
            if any(part in exclude_dirs for part in path.parts):
                continue

            if path.resolve() == script_path:
                continue

            if path.suffix in valid_extensions or path.name == 'Makefile':
                try:
                    content = path.read_text(encoding='utf-8')
                    if search_str in content:
                        new_content = content.replace(search_str, prefix)
                        path.write_text(new_content, encoding='utf-8')
                        modified_files.append(str(path.relative_to(root_dir)))
                except Exception as e:
                    print(f"Warning: Could not process {path}: {e}")

    if modified_files:
        print(f"\nSuccessfully replaced '{search_str}' with '{prefix}' in the following files:")
        for f in modified_files:
            print(f"  - {f}")
    else:
        print(f"\nNo occurrences of '{search_str}' found.")

if __name__ == "__main__":
    rename_template()
