import pathlib
import sys

import git

from ruamel.yaml import YAML

# typ="rt" → コメントを保持する
yaml = YAML(typ="rt")
# クォーテーションを保持する
yaml.preserve_quotes = True
# 折り返し防止
yaml.width = 4096

BATCH_YAML_PATH = "clubjt-cdk/def/batch/batch.yaml"
BATCH_2_YAML_PATH = "clubjt-cdk/def/batch/batch2.yaml"
BATCH_BPM_YAML_PATH = "clubjt-cdk/def/batch/batch_bpm.yaml"


class BatchYamlChecker:
    @classmethod
    def sort_batch_yaml(cls):
        """
        バッチ定義ファイルをソートし、バッチ名の長さをチェック
        pre-commit hookで実行（batch.yaml/batch2.yaml/batch_bpm.yamlの変更をトリガにする）
        """

        if len(sys.argv) < 2:
            print("[ERROR] バッチ定義ファイルパスの取得に失敗しました。チェックとソートを中断します。")
            sys.exit(1)

        print(f"[INFO] {sys.argv[1]}のチェックとソートを開始します。")

        definitions = cls._load_batch_definitions(yaml_path=sys.argv[1])

        is_error = False

        if batches := definitions.get("batches"):
            for batch_name, _ in batches.items():
                if len(f"clubjt-cron-{batch_name}-production") > 64:
                    print(
                        f"[ERROR] バッチ名は共通部分を含めて最大64文字になるよう設定してください。{batch_name}(clubjt-cron-{batch_name}-production)"
                    )
                    is_error = True

            # チェックエラーがなければソート
            if not is_error:
                definitions["batches"] = dict(sorted(batches.items()))
                with open(sys.argv[1], "w", encoding="utf-8") as f:
                    yaml.dump(definitions, f)

        print(f"[INFO] {sys.argv[1]}のチェックとソートを終了します。")

        exit(is_error)

    @classmethod
    def check_staged_batch_yaml_files(cls):
        """
        コミットメッセージをチェックし、特定の単語が含まれていないかつbatch.yamlがコミットされる場合は、コミットを中断
        commit-msg hookで実行（clubjt-server/.git/COMMIT_EDITMSGの変更をトリガにする）

        commit-msgで呼び出されるので、一度のコミットにつき一度だけ実行される。
        （pre-commitとは異なり、コミットするファイルの数だけ実行されることはない。）
        """

        if len(sys.argv) < 2:
            print("[ERROR] COMMIT_EDITMSGのパス取得に失敗しました。ソートを中断します。")
            sys.exit(1)

        repo = git.Repo(".")

        staged_batch_yaml_paths = [
            staged_file.a_path
            for staged_file in repo.index.diff("HEAD")
            if staged_file.a_path in [BATCH_YAML_PATH, BATCH_2_YAML_PATH, BATCH_BPM_YAML_PATH]
        ]

        if not staged_batch_yaml_paths:
            # batch.yaml/batch2.yaml/batch_bpn.yamlのどれにも変更が入っていなければチェックを実施しない
            exit(0)

        # clubjt-server/.git/COMMIT_EDITMSGに記載されたコミットメッセージに「batch.yaml変更」が含まれない場合は、batch.yamlのコミットを中断する。

        with open(sys.argv[1], "r", encoding="utf-8") as f:
            commit_message = f.read()

        if BATCH_YAML_PATH in staged_batch_yaml_paths and "batch.yaml変更" not in commit_message:
            print(
                "[ERROR] batch.yamlへ新しく定義を追加することは禁止されています。\n" \
                "batch2.yamlへ定義を記載してください。\n" \
                "※既存バッチの定義変更の場合のみ「batch.yaml変更」とコミットメッセージに記載してコミットしてください。\n"
            )
            exit(1)

        exit(0)

    @classmethod
    def _load_batch_definitions(cls, yaml_path: str):
        with open(yaml_path, "r", encoding="utf-8") as f:
            definitions = yaml.load(f)

        return definitions
