import sys


class PythonCodeChecker:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._messages: list[str] = []

        with open(file_path, "r", encoding="utf_8_sig") as f:
            self._source = f.read()

    def _check_uuid(self):
        if ("import uuid" in self._source and "uuid.uuid1()" in self._source) or (
            "from uuid import uuid1" in self._source and "uuid1()" in self._source
        ):
            self._messages.append(f"[ERROR] uuid.uuid1は使用禁止です: path={self._file_path}")

    def _check_static_method(self):
        if "@staticmethod" in self._source:
            self._messages.append(f"[ERROR] staticmethodは使用禁止です: path={self._file_path}")

    def check_all(self) -> list[str]:
        self._check_uuid()
        self._check_static_method()
        return self._messages


def main():
    if len(sys.argv) < 2:
        print("[ERROR] Pythonファイルが指定されていません")
        sys.exit(1)

    checker = PythonCodeChecker(file_path=sys.argv[1])
    messages = checker.check_all()

    for message in messages:
        print(message)

    if messages:
        sys.exit(1)
