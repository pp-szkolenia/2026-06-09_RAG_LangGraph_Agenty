import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pipeline import run_query


def print_answers(answers: list[dict]) -> None:
    for answer in answers:
        print(f"\n{'='*60}")
        print(f"## {answer['aspect_name']}")
        print("=" * 60)
        for para in answer["paragraphs"]:
            print(f"\n{para['response_paragraph_text']}")
            citations = ", ".join(
                f"{c['book_name']} {c['chapter_number']},{c['verse_number']}"
                for c in para["response_paragraph_citations"]
            )
            if citations:
                print(f"[{citations}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bible RAG pipeline")
    parser.add_argument("query", help="Question to ask about the Bible")
    parser.add_argument(
        "--level",
        choices=["basic", "medium", "deep"],
        default="medium",
        help="Analysis depth (default: medium)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print progress info for each pipeline step",
    )
    args = parser.parse_args()

    if args.debug:
        print(f"Query: {args.query}")
        print(f"Analysis level: {args.level}")
        print()

    answers = run_query(
        user_query=args.query,
        analysis_level=args.level,
        debug=args.debug,
    )

    print_answers(answers)


if __name__ == "__main__":
    main()
