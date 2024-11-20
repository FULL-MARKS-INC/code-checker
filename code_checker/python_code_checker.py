import re
import sys


class PythonCodeChecker:
    @classmethod
    def check_python_code(cls, file_path: str):
        with open(file_path, "r", encoding="utf_8_sig") as f:
            source = f.read()

        if ("import uuid" in source and "uuid.uuid1()" in source) or (
            "from uuid import uuid1" in source and "uuid1()" in source
        ):
            print(f"[ERROR] uuid.uuid1は使用禁止です: path={file_path}")
            return True

        if not file_path.endswith(("promotion_client.py", "user_client.py", "common_client.py")):
            if "@staticmethod" in source:
                print(f"[ERROR] staticmethodは使用禁止です: path={file_path}")
                return True

        if "logging.WARN" in source:
            print(f"[ERROR] logging.WARNではなくlogging.WARNINGを使用してください: path={file_path}")
            return True

        for log_level in ["[INFO]", "[WARN]", "[WARNING]", "[ERROR]"]:
            if log_level in source:
                print(f"[ERROR] ログレベル{log_level}はlevel引数に記載してください: path={file_path}")
                return True

        if "tests" not in file_path:
            common_date_evaluation = re.search(r"if.+\.(created_at|createdAt|updatedAt|updated_at).+", source)
            if common_date_evaluation:
                print(f"[ERROR] 評価実装にcreate_at/updated_atを使用しないでください: path={file_path}")
                return True

        return False

    @classmethod
    def check_todo_comments(cls):
        print(sys.argv)


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Pythonファイルが指定されていません")
        sys.exit(1)

    PythonCodeChecker.check_python_code(file_path=sys.argv[1])