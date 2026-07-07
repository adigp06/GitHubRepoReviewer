from url_parser import parse_github_url
from indexer import fetch_repo_contents
from cleaner import filter_codebase
import sys
from agent_core import run_agent_loop

def main():
    print("Welcome to the Autonomous Git Architecture Reviewer\n")
    repo_url = input("Please enter a public GitHub Repository URL: ").strip()

    if not repo_url:
        print("Repository URL cannot be empty")
        sys.exit(1)

    print("Initiizalizing engine componenets and mumti-agent swarm...")
    try:
        run_agent_loop(f"Review the architecture of the repo: {repo_url}")
    except Exception as e:
        print(f"\n System Error!:{e}")

if __name__ == "__main__":
    main()