import pathlib
import sys

import git

from ruamel.yaml import YAML

# typ="rt" → コメントを保持する
yaml = YAML(typ="rt")
# クォーテーションを保持する
yaml.preserve_quotes = True

BATCH_YAML_PATH = "clubjt-cdk/def/batch/batch.yaml"
BATCH_2_YAML_PATH = "clubjt-cdk/def/batch/batch2.yaml"


class BatchYamlChecker:
    @classmethod
    def check_batch_yaml_files(cls, commit_message_file_path: str):
        repo = git.Repo(".")

        staged_batch_yaml_paths = [
            staged_file.a_path
            for staged_file in repo.index.diff("HEAD")
            if staged_file.a_path in [BATCH_YAML_PATH, BATCH_2_YAML_PATH]
        ]

        if not staged_batch_yaml_paths:
            # batch.yamlとbatch.yamlのどちらも変更が入っていなければチェックを実施しない
            exit(0)

        # clubjt-server/.git/COMMIT_EDITMSGに記載されたコミットメッセージに「batch.yaml変更」が含まれない場合は、batch.yamlのコミットを中断する。

        with open(commit_message_file_path, "r", encoding="utf-8") as f:
            commit_message = f.read()

        if BATCH_YAML_PATH in staged_batch_yaml_paths and "batch.yaml変更" not in commit_message:
            print(
                "[ERROR] batch.yamlの変更は制限されています。batch2.yamlを変更するか、コミットメッセージに「batch.yaml変更」を記載してください。"
            )
            exit(1)

        is_error = False

        for staged_batch_yaml_paths in staged_batch_yaml_paths:
            is_error |= cls._check_batch_yaml(yaml_path=staged_batch_yaml_paths)

        sys.exit(is_error)

    @classmethod
    def _check_batch_yaml(cls, yaml_path: str) -> bool:
        print(f"[INFO] {yaml_path}のチェックとソートを開始します。")

        with open(yaml_path, "r", encoding="utf-8") as f:
            definition = yaml.load(f)

        is_error = False

        if batches := definition.get("batches"):
            batch_items = batches.items()

            for batch_name, _ in batch_items:
                if len(f"clubjt-cron-{batch_name}-production") > 64:
                    print(
                        f"[ERROR] バッチ名は共通部分を含めて最大64文字になるよう設定してください。{batch_name}(clubjt-cron-{batch_name}-production)"
                    )
                    is_error = True

            definition["batches"] = dict(sorted(batch_items))

            with open(yaml_path, "w", encoding="utf-8") as f2:
                yaml.dump(definition, f2)

        print(f"[INFO] {yaml_path}のチェックとソートを終了します。")

        return is_error


def main():
    """
    commit-msgで呼び出されるので、一度のコミットにつき一度だけ実行される。
    （pre-commitとは異なり、コミットするファイルの数だけ実行されることはない。）
    """

    if len(sys.argv) < 2:
        print("[ERROR] 引数が不足しています")
        sys.exit(1)

    BatchYamlChecker.check_batch_yaml_files(commit_message_file_path=sys.argv[1])