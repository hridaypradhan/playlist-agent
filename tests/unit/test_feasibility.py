from playlist_agent.environment import load_json
from playlist_agent.feasibility import check_basic_feasibility


def main() -> None:
    test_case = load_json("evaluation/cases/test_impossible.json")

    feasible, reason = check_basic_feasibility(test_case["constraints"])

    print(f"Feasible: {feasible}")
    print(f"Reason: {reason}")


if __name__ == "__main__":
    main()
