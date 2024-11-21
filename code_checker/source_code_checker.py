import re
import sys


class SourceCodeChecker:
    @classmethod
    def check_source_code(cls):
        """
        実装チェック
        pre-commit hookで実行
        """

        if len(sys.argv) < 2:
            print("[ERROR] 実装ファイルパスの取得に失敗しました。チェックを中断します。")
            sys.exit(1)

        print(f"{sys.argv[1]}のチェックを開始します。")

        source_code = cls._load_source_code()

        is_error = False

        if ("import uuid" in source_code and "uuid.uuid1()" in source_code) or (
            "from uuid import uuid1" in source_code and "uuid1()" in source_code
        ):
            print(f"[ERROR] uuid.uuid1は使用禁止です。")
            is_error = True

        if not file_path.endswith(("promotion_client.py", "user_client.py", "common_client.py")):
            if "@staticmethod" in source_code:
                print(f"[ERROR] staticmethodは使用禁止です。")
                is_error = True

        if "logging.WARN" in source_code:
            print(f"[ERROR] logging.WARNではなくlogging.WARNINGを使用してください。")
            is_error = True

        for log_level in ["[INFO]", "[WARN]", "[WARNING]", "[ERROR]"]:
            if log_level in source_code:
                print(f"[ERROR] ログレベル{log_level}はlevel引数に記載してください。")
                is_error = True

        if "tests" not in file_path:
            common_date_evaluation = re.search(r"if.+\.(created_at|createdAt|updatedAt|updated_at).+", source_code)
            if common_date_evaluation:
                print(f"[ERROR] 評価実装にcreate_at・updated_atを使用しないでください。")
                is_error = True

        print(f"{sys.argv[1]}のチェックを終了します。")

        exit(is_error)

    @classmethod
    def check_merged_source_code(cls):
        """
        production/stage/MAINブランチにマージする実装にTODOコメントが残っているかをチェック
        pre-merge-commit hookで実行
        """

        if len(sys.argv) < 2:
            print("[ERROR] チェック対象ファイルのパス取得に失敗しました。チェックを中断します。")
            sys.exit(1)

        print(f"{sys.argv[1]}マージ前チェックを開始します。")

        source_code = cls._load_source_code()

        if "TODO" in source_code:
            print("[ERROR] TODOコメントを削除してください。")
            exit(1)

        print(f"{sys.argv[1]}マージ前チェックを終了します。")

    @classmethod
    def _load_source_code(cls):
        with open(file_path, "r", encoding="utf_8_sig") as f:
            code = f.read()

        return code


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Pythonファイルが指定されていません")
        sys.exit(1)

    PythonCodeChecker.check_python_code(file_path=sys.argv[1])