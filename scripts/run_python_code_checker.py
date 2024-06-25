import ast
import json
import os

from code_checker.python_code_checker import PythonCodeChecker
from scripts.py_file_finder import PyFileFinder


class OperationPythonCodeCheck:
    """
    pythonコードチェックの動作確認
    """

    @classmethod
    def run(cls):
        for check_target_path in PyFileFinder.find_py_file_paths():
            PythonCodeChecker.check_python_code(file_path=check_target_path)


if __name__ == "__main__":
    OperationPythonCodeCheck.run()