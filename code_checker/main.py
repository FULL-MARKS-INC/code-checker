import sys

from code_checker.python_code_checker import PythonCodeChecker


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Pythonファイルが指定されていません")
        sys.exit(1)

    checker = PythonCodeChecker(file_path=sys.argv[1])
    messages = checker.check_all()

    for message in messages:
        print(message)

    if messages:
        sys.exit(1)
