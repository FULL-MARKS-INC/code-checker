from code_checker.python_code_checker import PythonCodeChecker

# pre-commitに組み込む前に、直接チェック・ソートを実行して動作確認


def check_module_client_source():
    module_dir_path = "C:\\Users\\umeza\\Documents\\donuts-root\\clubjt-server\\clubjt-impl\\clubjt_impl\\module"

    PythonCodeChecker.check_python_code(file_path=f"{module_dir_path}/promotion_client.py")


if __name__ == "__main__":
    check_module_client_source()