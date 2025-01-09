import re
import subprocess
import sys

import git


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

        print(sys.argv)

        print(f"{sys.argv[1]}のチェックを開始します。")

        source_code = cls._load_source_code(file_path=sys.argv[1])

        is_error = False

        if ("import uuid" in source_code and "uuid.uuid1()" in source_code) or (
            "from uuid import uuid1" in source_code and "uuid1()" in source_code
        ):
            print(f"[ERROR] uuid.uuid1は使用禁止です。")
            is_error = True

        if "@staticmethod" in source_code:
            print(f"[ERROR] staticmethodは使用禁止です。")
            is_error = True

        # if re.match(r"^logging.WARN$", source_code):
        #     print(f"[ERROR] logging.WARNではなくlogging.WARNINGを使用してください。")
        #     is_error = True

        for log_level in ["[INFO]", "[WARN]", "[WARNING]", "[ERROR]"]:
            if log_level in source_code:
                print(f"[ERROR] ログレベル{log_level}はlevel引数に記載してください。")
                is_error = True

        if re.search(r"(if|elif).+\.(created_at|createdAt|updatedAt|updated_at).+", source_code):
            print(f"[ERROR] if・elifでcreate_at・updated_atの値を比較しないでください。")
            is_error = True

        # 指定したファイルの差分に `# type: ignore` が含まれているかチェック
        diff = subprocess.run(["git", "diff", "--cached", sys.argv[1]], capture_output=True, text=True)
        print(diff)
        if bool(re.search(r"#\s*type:\s*ignore", diff.stdout)):
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

        print(f"{sys.argv[1]}のマージ前チェックを開始します。")

        source_code = cls._load_source_code(file_path=sys.argv[1])

        if "TODO" in source_code:
            repo = git.Repo(".")
            if repo.active_branch.name in ["production", "stage"] or repo.active_branch.name.endswith(
                "/GEN4_PROGRAM_UPDATE-MAIN"
            ):
                print("[ERROR] production/stage/*-MAINブランチにマージするには、TODOコメントを削除してください。")
                exit(1)

        print(f"{sys.argv[1]}のマージ前チェックを終了します。")

    @classmethod
    def _load_source_code(cls, file_path: str):
        with open(file_path, "r", encoding="utf_8") as f:
            code = f.read()

        return code
