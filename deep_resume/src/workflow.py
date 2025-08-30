import asyncio
import logging
from src.graph import build_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """Enable debug level logging for more detailed execution information."""
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()


async def run_agent_workflow_async(
    user_input: str,
    debug: bool = False,
    max_analyst_iterations: int=3,
    max_step_num: int=3,
):
    """Run the agent workflow asynchronously with the given user input.

    Args:
        user_input: The user's query or request
        debug: If True, enables debug level logging
        max_analyst_iterations: Maximum number of analyst iterations
        max_step_num: Maximum number of steps in a report

    Returns:
        The final state after the workflow completes
    """
    if not user_input:
        raise ValueError("Input could not be empty")

    if debug:
        enable_debug_logging()

    logger.info(f"Starting async workflow with user input: {user_input}")
    initial_state = {
        # Runtime Variables
        "resume_file_path": user_input,
    }
    config = {
        "configurable": {
            "max_analyst_iterations": max_analyst_iterations,
            "max_step_num": max_step_num,
        },
        "recursion_limit": 100,
    }
    last_message_cnt = 0
    async for s in graph.astream(
        input=initial_state, config=config, stream_mode="values"
    ):
        try:
            if isinstance(s, dict) and "messages" in s:
                if len(s["messages"]) <= last_message_cnt:
                    continue
                last_message_cnt = len(s["messages"])
                message = s["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
            else:
                # For any other output format
                print(f"Output: {s}")
        except Exception as e:
            logger.error(f"Error processing stream output: {e}")
            print(f"Error processing output: {str(e)}")

    logger.info("Async workflow completed successfully")


if __name__ == "__main__":
    print(graph.get_graph(xray=True).draw_mermaid())
