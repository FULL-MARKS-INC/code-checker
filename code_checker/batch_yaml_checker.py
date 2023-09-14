import sys
import yaml


class BatchYamlChecker:
    def __init__(self, file_path: str):
        with open(file_path, "r") as f:
            self.batch_definitions = yaml.load(f, Loader=yaml.SafeLoader).get("batchs")

    def check_batch_definitions(self):
        is_exceeded_batch_name_character_number = False

        for batch_name in self.batch_definitions():
            if len(batch_name) > 48:
                print(f"[ERROR] バッチ名は最大48文字にしてください。{batch_name}")

        sys.exit(int(is_exceeded_batch_name_character_number))


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Batch定義のYamlファイルが指定されていません")
        sys.exit(1)

    checker = BatchYamlChecker(file_path=sys.argv[1])
    checker.check_batch_definitions()