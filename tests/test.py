import os
import sys
import difflib

from src.Translate import translate


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
SKELETON_DIR = os.path.join(SRC_DIR, "skeletons")


def normalize_code(code: str) -> list[str]:
    lines = code.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.rstrip() for line in lines]

    # strip leading blank lines
    while lines and lines[0] == "":
        lines.pop(0)

    # strip trailing blank lines
    while lines and lines[-1] == "":
        lines.pop()

    return lines


def get_supported_languages() -> list[str]:
    languages = []
    for filename in os.listdir(SKELETON_DIR):
        if filename.endswith(".skeleton"):
            languages.append(filename.removesuffix(".skeleton"))
    return sorted(languages)


def read_code_file(language: str) -> str:
    path = os.path.join(PROJECT_ROOT, f"{language}.code")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing code file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def print_side_by_side_diff(expected: list[str], actual: list[str]):
    diff = difflib.ndiff(expected, actual)

    print("\nExpected | Actual")
    print("-" * 80)
    for line in diff:
        tag = line[:2]
        content = line[2:]

        if tag == "  ":
            print(f"{content:<38} | {content}")
        elif tag == "- ":
            print(f"{content:<38} |")
        elif tag == "+ ":
            print(f"{'':<38} | {content}")
    print("-" * 80)
    print()


def main():
    languages = get_supported_languages()

    if len(languages) < 2:
        print("Not enough languages found to run translation tests.")
        return

    passes = 0
    failures = 0

    for from_lang in languages:
        input_code = read_code_file(from_lang)

        for to_lang in languages:
            if from_lang == to_lang:
                continue

            label = f"{from_lang.capitalize()} to {to_lang.capitalize()}"
            print(f"{label:.<30}", end="")

            translated = translate(from_lang, to_lang, input_code)
            expected = read_code_file(to_lang)

            norm_translated = normalize_code(translated)
            norm_expected = normalize_code(expected)

            if norm_translated == norm_expected:
                print("Passed")
                passes += 1
            else:
                print("Failed")
                failures += 1
                print_side_by_side_diff(norm_expected, norm_translated)

    total = passes + failures

    print("\nSummary:")
    print(f"  Passed: {passes}")
    print(f"  Failed: {failures}")
    print(f"  Total : {total}")

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
