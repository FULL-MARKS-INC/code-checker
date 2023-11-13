from code_checker.batch_yaml_checker import BatchYamlChecker

# pre-commitに組み込む前に、直接チェック・ソートを実行して動作確認

if __name__ == "__main__":
    YAMl_PATH = "C:\\Users\\umeza\\Documents\\donuts-root\\clubjt-server\\clubjt-cdk\\def\\batch\\batch.yaml"
    BatchYamlChecker.check_batch_yaml(yaml_path=YAMl_PATH)