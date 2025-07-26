"""
Script to scan for exposed SmartThings tokens in the repository.
Searches for patterns matching UUID-like tokens and common variable names.
"""
import os
import re

# Regex for UUID-like SmartThings tokens
TOKEN_REGEX = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
# Common variable names for tokens
TOKEN_NAMES = ['SMARTTHINGS_TOKEN', 'DEFAULT_TOKEN', 'access_token', 'token']


def scan_file(filepath):
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                # Only report UUID-like tokens
                for match in TOKEN_REGEX.findall(line):
                    results.append((filepath, i, match, line.strip()))
    except Exception as e:
        results.append((filepath, 'ERROR', str(e), ''))
    return results


def scan_repo(root_dir):
    findings = []
    skip_dirs = {'.venv', 'venv', 'ENV', '__pycache__'}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove skip_dirs from dirnames so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                findings.extend(scan_file(filepath))
    return findings


def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    findings = scan_repo(repo_dir)
    if findings:
        # Build concise report: {script name} {token}
        report = {}
        for filepath, _, token, _ in findings:
            script = os.path.basename(filepath)
            if script not in report:
                report[script] = set()
            report[script].add(token)
        print("Exposed token summary (UUID tokens only):")
        for script, tokens in report.items():
            for token in tokens:
                print(f"- {script} {token}")
    else:
        print("No exposed tokens found.")

if __name__ == "__main__":
    main()
