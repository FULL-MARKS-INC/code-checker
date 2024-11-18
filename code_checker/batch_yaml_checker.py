import sys

from ruamel.yaml import YAML

# typ="rt" → コメントを保持する
yaml = YAML(typ="rt")
# クォーテーションを保持する
yaml.preserve_quotes = True


class BatchYamlChecker:
    @classmethod
    def check_batch_yaml(cls, yaml_path: str):
        with open(yaml_path, "r") as f:
            definition = yaml.load(f)

        is_error = False

        print("[INFO] バッチ定義YAMLファイルのチェックとソートを開始します。")

        if batches := definition.get("batches"):
            batch_items = batches.items()

            for batch_name, _ in batch_items:
                if len(f"clubjt-cron-{batch_name}-production") > 64:
                    print(f"[ERROR] バッチ名は共通部分を含めて最大64文字になるよう設定してください。{batch_name}(clubjt-cron-{batch_name}-production)")
                    is_error = True

            definition["batches"] = dict(sorted(batch_items))

            with open(yaml_path, "w", encoding="utf-8") as f2:
                yaml.dump(definition, f2)

        print("[INFO] バッチ定義YAMLファイルのチェックとソートを終了します。")

        sys.exit(int(is_error))


def main():
    import pathlib
    print(pathlib.Path(__file__))
    exit(1)
    if len(sys.argv) < 2:
        print("[ERROR] Batch定義のYamlファイルが指定されていません")
        sys.exit(1)

    BatchYamlChecker.check_batch_yaml(yaml_path=sys.argv[1])