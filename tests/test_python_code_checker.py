from code_checker.python_code_checker import PythonCodeChecker


class TestPythonCodeChecker:
    def test_check_all(self):
        checker = PythonCodeChecker(file_path="./tests/code/target_1.py")
        messages = checker.check_all()

        assert len(messages) == 1
        assert messages[0] == "[ERROR] uuid.uuid1は使用禁止です: path=./tests/code/target_1.py"

        checker = PythonCodeChecker(file_path="./tests/code/target_2.py")
        messages = checker.check_all()

        assert len(messages) == 2
        assert messages[0] == "[ERROR] uuid.uuid1は使用禁止です: path=./tests/code/target_2.py"
        assert messages[1] == "[ERROR] staticmethodは使用禁止です: path=./tests/code/target_2.py"
