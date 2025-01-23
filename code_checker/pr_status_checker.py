import os
import subprocess
import json
import time
from datetime import datetime


class PRStatusChecker:
    @classmethod
    def check_pr_status(cls) -> int:
        print("GitHub PR Checker を開始します...", datetime.now().isoformat())

        time.sleep(3)
        try:
            # ブランチ名の抽出
            branch_name = cls._get_source_branch()
            if not branch_name:
                print("マージ中ではありません。スキップします。")
                cls.reset_to_before_merge()
                return 1

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
        if not os.environ.get("GIT_REFLOG_ACTION", "").startswith("merge "):
            print("マージ処理中ではありません。スキップします。")
            return None

        merged_branch_name = os.environ.get("GIT_REFLOG_ACTION", "").removeprefix("merge ")
        return merged_branch_name

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
            if not is_fms_member:
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
        """PRのコミットが全てFMs社員のものか判定"""
        results = cls._run_command(["gh", "pr", "view", pr_number, "--json", "commits"])
        commits = json.loads(results)["commits"]

        commit_author_emails = []
        for commit in commits:
            # parentsの数が1より大きい場合はマージコミットなのでスキップ
            if len(commit["parents"]) > 1:
                continue

            for author in commit["authors"]:
                commit_author_emails.append(author["email"])

        return all([email for email in commit_author_emails if email.find("@fullmarks.co.jp")])
