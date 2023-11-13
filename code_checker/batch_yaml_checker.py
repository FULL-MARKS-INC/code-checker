import re
import sys

import yaml


def represent_str(dumper, instance):
    if "\n" in instance:
        instance = "\n".join([line.rstrip() for line in instance.splitlines()])
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance, style="|")
    elif re.match(MATCH_REGEX, instance) or re.search(SEARCH_REGEX, instance):
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance, style="'")
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance)


yaml.add_representer(str, represent_str, Dumper=yaml.CSafeDumper)

MATCH_REGEX = re.compile(r"[&*#!?|\-<>=%@]")
SEARCH_REGEX = re.compile(r"[\[\]{}:\"]")


class BatchYamlChecker:
    @classmethod
    def check_batch_yaml(cls, yaml_path: str):
        with open(yaml_path, "r") as f:
            definition = yaml.load(f, Loader=yaml.SafeLoader)

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
    if len(sys.argv) < 2:
        print("[ERROR] Batch定義のYamlファイルが指定されていません")
        sys.exit(1)

    BatchYamlChecker.check_batch_yaml(yaml_path=sys.argv[1])