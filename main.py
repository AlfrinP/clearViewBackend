import argparse
import json
import logging

from crew import run_fake_news_pipeline


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    parser = argparse.ArgumentParser(description="CrewAI fake news detection")
    parser.add_argument(
        "--news",
        type=str,
        help="News text to analyze. If omitted, interactive prompt is used.",
    )
    args = parser.parse_args()

    news_text = args.news or input("Enter news text to verify: ").strip()
    if not news_text:
        raise ValueError("News text cannot be empty.")

    result = run_fake_news_pipeline(news_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()