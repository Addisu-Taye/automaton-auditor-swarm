from src.graph import build_auditor_graph
from dotenv import load_dotenv

load_dotenv()


def main():
    """Main entry point for the Automaton Auditor Swarm."""
    app = build_auditor_graph()
    
    # Example Input
    input_state = {
        "repo_url": "https://github.com/example/target_repo",
        "pdf_path": None,
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": [],
        "final_report": "",
        "errors": []
    }
    
    result = app.invoke(input_state)
    print(result["final_report"])


if __name__ == "__main__":
    main()
