import os
import re
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path


class PRStatusChecker:
    @classmethod
    def check_pr_status(cls) -> int:
        print("GitHub PR Checker を開始します...")

        time.sleep(3)
        try:
            # ブランチ名の抽出
            branch_name = cls._get_source_branch()
            if not branch_name:
                print("マージ中ではありません。スキップします。")
                return 0

            # PRのステータスチェック
            success = cls._check_pr_status(branch_name)
            if not success:
                print("\nPRの概要欄を確認後チェックをつけてください。")
                print("\nPushを中断します。")
                cls.reset_to_before_merge()
                return 1

            print("\nPRのステータスはSUCCESSです。Pushします。")
            return 0

        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            cls.reset_to_before_merge()
            return 1

    @classmethod
    def _run_command(cls, command: list) -> str:
        """コマンドを実行して結果を返す"""
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()

    @classmethod
    def _get_source_branch(cls) -> str | None:
        """マージ元のブランチ名取得"""
        git_dir = cls._run_command(["git", "rev-parse", "--git-dir"])
        merge_msg_file = os.getcwd() / Path(git_dir) / "MERGE_MSG"

        if not merge_msg_file.exists():
            return None

        merge_msg = merge_msg_file.read_text()

        match = re.search(r"Merge\s+branch\s+'([^']+)'", merge_msg)
        if match:
            return match.group(1)
        return None

    @classmethod
    def _check_gh_cli(cls) -> bool:
        """GitHub CLIが利用可能か確認"""
        # GitHub CLIの存在確認
        if subprocess.run(["which", "gh"], capture_output=True).returncode != 0:
            print("エラー: GitHub CLI (gh) がインストールされていません")
            cls.reset_to_before_merge()
            return False

        # 認証状態の確認
        if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
            print("エラー: GitHub CLIが認証されていません")
            print("gh auth login を実行してログインしてください")
            cls.reset_to_before_merge()
            return False

        return True

    @classmethod
    def _check_pr_status(cls, branch_name: str) -> bool:
        """PRのステータスをチェック"""
        # GitHub CLIのチェック
        if not cls._check_gh_cli():
            return False

        print(f"\nブランチ '{branch_name}' のPRを検索しています...")

        try:
            # PRの検索
            pr_list = cls._run_command(["gh", "pr", "list", "--head", branch_name, "--json", "number"])
            prs = json.loads(pr_list)

            if not prs:
                print(f"警告: ブランチ {branch_name} のPRが見つかりません")
                return True

            pr_number = prs[0]["number"]

            is_fms_member = cls.is_fms_member(str(pr_number))
            if not is_fms_member: # FMs社員ではない場合はステータスチェックを常にTrueで通過
                return True

            print(f"PR #{pr_number} のステータスチェックを確認しています...")

            # ステータスチェックの取得
            status_json = cls._run_command(["gh", "pr", "view", str(pr_number), "--json", "statusCheckRollup"])
            status_data = json.loads(status_json).get("statusCheckRollup", None)

            if not status_data:
                return True

            latest_conclusion = max(
                status_data, key=lambda x: datetime.fromisoformat(x["completedAt"].replace("Z", ""))
            ).get("conclusion", False)

            # FAILURE以外（SKIPも）はSUCCESSとみなす
            return not latest_conclusion == "FAILURE"

        except subprocess.CalledProcessError as e:
            print(f"GitHub CLIコマンドの実行中にエラーが発生: {e}")
            return False

    @classmethod
    def reset_to_before_merge(cls):
        """差分を破棄して前の作業ブランチに戻る"""
        print("git reset --mergeを実行してgit statusリセット後に再試行してください。")

        cls._run_command(["git", "reset", "--merge"])

        cls._run_command(["git", "checkout", "-"])

    @classmethod
    def is_fms_member(cls, pr_number: str):
        """PRのコミットの1番初めがFMs社員のコミットか確認"""
        results = cls._run_command(["gh", "pr", "view", pr_number, "--json", "commits"])
        commits = json.loads(results)["commits"]
        for commit in commits:
            if commit["messageHeadline"] and commit["messageHeadline"].find("Merge"):
                continue

            return commit["authors"][0]["email"].find("@fullmarks.co.jp")
