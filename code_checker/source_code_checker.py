import re
import os
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

        is_error = False
        for filepath in sys.argv[1:]:
            print(f"{filepath}のチェックを開始します。")

            source_code = cls._load_source_code(file_path=filepath)

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

            # if re.search(r"(if|elif).+\.(created_at|createdAt|updatedAt|updated_at).+", source_code):
            #     print(f"[WARNING] if・elifでcreate_at・updated_atの値を比較しないでください。")

            # if re.search(r"Entity¥.[a-zA-Z0-9_]¥.+is_¥(", source_code):
            #     print(f"[ERROR] Entity.column.is_(...)を使用しないでください。")
            #     is_error = True

            # ファイルの差分に `# type: ignore` が含まれているかチェック
            if filepath.endswith(".py"):
                repo = git.Repo(".")
                diff_output = repo.git.diff('--cached', '-U0', filepath)

                added_lines = [line[1:] for line in diff_output.splitlines() if line.startswith("+") and not line.startswith("+++")]

                violations = [line for line in added_lines if bool(re.search(r"#\s*type:\s*ignore", line))]

                if violations:
                    print("[ERROR] `# type: ignore` を追加しないでください", file=sys.stderr)
                    for line in violations:
                        print(f"+ {line.strip()}", file=sys.stderr)
                    is_error = True

            print(f"{filepath}のチェックを終了します。")

            if is_error:
                exit(is_error)

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
