from pathlib import Path
import argparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]


parser = argparse.ArgumentParser()

parser.add_argument(
    "--term",
    required=True
)

args = parser.parse_args()


search_dirs = [
    PROJECT_ROOT / "queries",
    PROJECT_ROOT / "shapes",
    PROJECT_ROOT / "mappings",
    PROJECT_ROOT / "src",
]


extensions = {
    ".rq",
    ".ttl",
    ".csv",
    ".py",
    ".cypher",
    ".md",
}


matches: list[str] = []


for directory in search_dirs:

    if not directory.exists():
        continue

    for file in directory.rglob("*"):

        if (
            file.is_file()
            and file.suffix in extensions
        ):

            try:

                text = file.read_text(
                    encoding="utf-8"
                )

            except UnicodeDecodeError:
                continue


            if args.term in text:

                matches.append(
                    str(
                        file.relative_to(
                            PROJECT_ROOT
                        )
                    )
                )


print("=" * 70)
print("CONCEPT DEPENDENCY SEARCH")
print("=" * 70)

print(
    f"Term: {args.term}"
)

print(
    f"Files found: {len(matches)}"
)


for file in matches:

    print(
        f"- {file}"
    )
