import pathlib
import sys

from ruamel.yaml import YAML

# typ="rt" → コメントを保持する
yaml = YAML(typ="rt")
# クォーテーションを保持する
yaml.preserve_quotes = True


class BatchYamlChecker:
    @classmethod
    def check_batch_yaml(cls, commit_message_file_path: str):
        # clubjt-server/.git/COMMIT_EDITMSGに記載されたコミットメッセージに「batch.yaml変更」が含まれない場合は、batch.yamlのコミットを中断する。
 
        with open(commit_message_file_path, "r") as f:
            commit_message = f.read()

        if yaml_path.endswith("batch.yaml") and "batch.yaml変更" not in commit_message:
            print(
                "[ERROR] batch.yamlの変更は制限されています。batch2.yamlを変更するか、コミットメッセージに「batch.yaml変更」を記載してください。"
            )
            exit(1)

        with open(yaml_path, "r") as f:
            definition = yaml.load(f)

        is_error = False

        print("[INFO] バッチ定義YAMLファイルのチェックとソートを開始します。")

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

        print("[INFO] バッチ定義YAMLファイルのチェックとソートを終了します。")

        sys.exit(int(is_error))


def main():
    """
    commit-msgで呼び出されるので、一度のコミットにつき一度だけ実行される。
    （pre-commitとは異なり、コミットするファイルの数だけ実行されることはない。）
    """

    if len(sys.argv) < 2:
        print("[ERROR] 引数が不足しています")
        sys.exit(1)

    # BatchYamlChecker.check_batch_yaml(commit_message_file_path=sys.argv[1])
    print(sys.argv)
    exit(1)


if __name__ == "__main__":
    main()