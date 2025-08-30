import argparse
import asyncio
from src.workflow import run_agent_workflow_async

def ask(
    question,
    debug=False,
    max_analyst_iterations=3,
    max_step_num=3,
):
    """Run the agent workflow with the given question.

    Args:
        question: The user's query or request
        debug: If True, enables debug level logging
        max_analyst_iterations: Maximum number of analyst iterations
        max_step_num: Maximum number of steps in a report
    """
    asyncio.run(
        run_agent_workflow_async(
            user_input=question,
            debug=debug,
            max_analyst_iterations=max_analyst_iterations,
            max_step_num=max_step_num,
        )
    )

if __name__ == "__main__":
        # Set up argument parser
    parser = argparse.ArgumentParser(description="Run the DeepResume")
    parser.add_argument("query", nargs="*", help="The query to process")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--max_analyst_iterations",
        type=int,
        default=3,
        help="Maximum number of analyst iterations (default: 3)",
    )
    parser.add_argument(
        "--max_step_num",
        type=int,
        default=3,
        help="Maximum number of steps in a report (default: 3)",
    )
    args = parser.parse_args()

    if args.query:
        user_query = " ".join(args.query)
    else:
        user_query = input("Enter your resume pdf path: ")
    
    ask(
        question=user_query,
        debug=args.debug,
        max_analyst_iterations=args.max_analyst_iterations,
        max_step_num=args.max_step_num,
    )