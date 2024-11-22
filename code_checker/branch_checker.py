import os
import re

import git


class BranchChecker:
    @classmethod
    def check_merge_branch(cls):
        """
        マージブランチを制限する
        pre-merge-commit hookで実行
        """

        repo = git.Repo(".")

        # 先頭の"merge"を除いた文字列がブランチ名
        merged_branch_name = os.environ.get("GIT_REFLOG_ACTION", "").removeprefix("merge ")

        if repo.active_branch.name == "sweets/PRE/GEN4_PROGRAM_UPDATE-MAIN":
            if not re.match(r"^(origin/)?(production|sweets/PRE/GEN4_PROGRAM_UPDATE-(?!.*MAIN).+)$", merged_branch_name):
                print("sweets/PRE/GEN4_PROGRAM_UPDATE-MAINへのマージは、productionかsweets/PRE/GEN4_PROGRAM_UPDATE-*からのみ可能です。")
                exit(1)

        if re.match(r"^sweets/PRE/GEN4_PROGRAM_UPDATE-(?!.*MAIN).+$", repo.active_branch.name):
            if not re.match(r"^(origin/)?sweets/PRE/GEN4_PROGRAM_UPDATE-MAIN$", merged_branch_name):
                print("sweets/PRE/GEN4_PROGRAM_UPDATE-*へのマージは、sweets/PRE/GEN4_PROGRAM_UPDATE-MAINからのみ可能です。")
                exit(1)

        if repo.active_branch.name == "sweets/POST/GEN4_PROGRAM_UPDATE-MAIN":
            if not re.match(r"^(origin/)?(production|sweets/POST/GEN4_PROGRAM_UPDATE-(?!.*MAIN).+)$", merged_branch_name):
                print("sweets/POST/GEN4_PROGRAM_UPDATE-MAINへのマージは、productionかsweets/POST/GEN4_PROGRAM_UPDATE-*からのみ可能です。")
                exit(1)

        if re.match(r"^sweets/POST/GEN4_PROGRAM_UPDATE-(?!.*MAIN).+$", repo.active_branch.name):
            if not re.match(r"^(origin/)?sweets/POST/GEN4_PROGRAM_UPDATE-MAIN$", merged_branch_name):
                print("sweets/POST/GEN4_PROGRAM_UPDATE-*へのマージは、sweets/POST/GEN4_PROGRAM_UPDATE-MAINからのみ可能です。")
                print(1)
