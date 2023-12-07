from subprocess import STDOUT, check_output
import argparse
import os

parser=argparse.ArgumentParser()

parser.add_argument("--pull_request_id", required=True, type=int)

args=parser.parse_args()

rst_dir = "docs/upcoming_changes"
types_of_changes = ["highlight",
                    "np_support",
                    "deprecation",
                    "expired",
                    "compatibility",
                    "cuda",
                    "new_feature",
                    "improvement",
                    "performance",
                    "change",
                    "doc",
                    "infrastructure",
                    "bug_fix"]

def list_rst_filename() -> str:
    output = check_output(
        ["git", "diff", "--name-only", "origin/main"],
        encoding="utf-8",
        stderr=STDOUT,
    )

    all_files = output.strip().splitlines()
    rst_file = [file for file in all_files if 
                file.startswith(rst_dir + "/" + str(args.pull_request_id) + ".")]
    assert len(rst_file) == 1, "There must be a relevant .rst file added in the PR. " + \
        "Filename must start with the respective Pull Request ID" + \
        " (eg 1234. for PR #1234) followed by a . character"
    return rst_file[0]

file = list_rst_filename()
print(f"Checking {file}")
# Must be an .rst file
assert file.endswith(".rst"), "File must be a .rst file"
# Must start file name with the PR number, followed by a ".",
# followed by type of change
filename = file.split("/")[-1]

all_towncrier_rst = os.listdir(rst_dir)
all_towncrier_rst = [rst for rst in all_towncrier_rst 
                     if not (rst.startswith("template")
                             or rst.startswith("README"))]
all_pr_ids = [int(rst.split(".")[0]) for rst in all_towncrier_rst]
assert len(set(all_pr_ids)) == len(all_pr_ids), \
    "All PR IDs must be unique. Please check for duplicate PR IDs"

assert len(filename.split(".")) == 3, \
    "Filename must be in the format <PR_ID>.<type_of_change>.rst"

# Must be one of the required types of changes
assert filename.split(".")[1] in types_of_changes, \
    "File must be one of the following types of changes:" + \
    " highlight, np_support, deprecation, expired, compatibility" + \
    ", cuda, new_feature, improvement, performance, change, doc" + \
    ", infrastructure, bug_fix"
print(f"Passed: Filename is valid")

# Check rst contents
with open(file, "r") as f:
    contents = f.read().splitlines()
    # First line must be the title followed by the underline
    assert len(contents) >= 4, "File must have at least four lines"
    title = contents[0]
    assert len(title) > 0, "Title must not be empty"
    underline = contents[1]
    for underline_type in underline:
        assert underline_type == "=", "Header should be underlined with = characters"
    assert len(title) == len(underline), "Title and underline must be the same length." + \
        f" (Found Title: {len(title)}, Underline: {len(underline)})"
    blank_line = contents[2]
    assert len(blank_line) == 0, "Third line must be blank"
    description = contents[3]
    assert len(description) > 0, "Description must not be empty"
    print(f"Passed: File contents are valid")

output = check_output(["rstcheck", file], stderr=STDOUT, encoding="utf-8")
assert "Success! No issues detected." in output, \
    "File is not a valid .rst file. Please check for errors using rstcheck"
print(f"Passed: rstcheck passed")
