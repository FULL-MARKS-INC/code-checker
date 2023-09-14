import sys
import yaml


class BatchYamlChecker:
    def __init__(self, file_path: str):
        with open(file_path, "r") as f:
            self.batch_definitions = yaml.load(f, Loader=yaml.SafeLoader).get("batchs") or []

    def check_batch_definitions(self):
        print("[INFO] バッチ定義YAMLファイルのチェックを開始します。")

        is_exceeded_batch_name_character_number = False

        for batch_name in self.batch_definitions:
            if len(batch_name) > 48:
                print(f"[ERROR] バッチ名は最大48文字にしてください。{batch_name}")
                is_exceeded_batch_name_character_number = True

        print("[INFO] バッチ定義YAMLファイルのチェックを終了します。")

        sys.exit(int(is_exceeded_batch_name_character_number))


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Batch定義のYamlファイルが指定されていません")
        sys.exit(1)

    checker = BatchYamlChecker(file_path=sys.argv[1])
    checker.check_batch_definitions()