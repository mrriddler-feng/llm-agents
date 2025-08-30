import logging, json
from typing import Literal

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langchain_community.document_loaders.pdf import PyPDFLoader

from src.tools.search import LoggedTavilySearch
from src.tools import web_search_tool
from .types import State
from ..config import SEARCH_MAX_RESULTS, SELECTED_SEARCH_ENGINE, SearchEngine
from ..config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_by_type
from src.prompts.template import apply_prompt_template
from src.prompts.resume_model import Resume
from src.prompts.report_model import Report
from src.utils.json_utils import repair_json_output
from src.agents.agents import research_agent
from src.prompts.topic_generator import generate_topic_list, generate_report
from src.config.configuration import Configuration

logger = logging.getLogger(__name__)

def reviewer_node(state: State):

    if not state.get("resume_file_path"):
        logger.error(
            f"State has not valid resume_file_path"
        )
        return Command(goto="__end__")

    loader = PyPDFLoader(
        file_path = state["resume_file_path"],
        mode = "single",
        pages_delimiter = "\n\f",
    )
    documents = loader.load()
    page_contents = []
    for do in documents:
        page_contents.append(do.page_content)

    resume_str = "\n".join(page_contents)
    resume_str = resume_str.replace("\n", " ")

    if len(resume_str) == 0:
        logger.error(
            f"Resume content is empty after loading from {state['resume_file_path']}"
        )
        return Command(goto="__end__")

    messages = apply_prompt_template("reviewer", state)

    messages += [
            {
                "role": "user",
                "content": (
                    "The resume content is: "
                    + resume_str
                ),
            }
        ]
    
    if AGENT_LLM_MAP["reviewer"] == "basic":
        llm = get_llm_by_type(AGENT_LLM_MAP["reviewer"]).with_structured_output(
            Resume,
            method="json_mode",
        )
    else:
        llm = get_llm_by_type(AGENT_LLM_MAP["reviewer"])
    
    full_response = ""
    if AGENT_LLM_MAP["reviewer"] == "basic":
        response = llm.invoke(messages)
        full_response = response.model_dump_json(indent=4, exclude_none=True)
    else:
        response = llm.stream(messages)
        for chunk in response:
            full_response += chunk.content

    try:
        full_response = repair_json_output(full_response)
        resume_json = json.loads(full_response)
    except json.JSONDecodeError:
        logger.warning("reviewer response is not a valid JSON")
        return Command(goto="__end__")
    
    resume = Resume.model_validate(resume_json)
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Reviewer response: {resume}")
    return Command(
        update={
            "resume": resume,
        },
        goto="coordinator",
    )

def coordinator_node(state: State, config: RunnableConfig) -> Command[Literal["background_investigator", "analyst", "researcher"]]:
    topic_list = state.get("topic_list", [])
    topic_idx = state.get("topic_idx", -1)
    configurable = Configuration.from_runnable_config(config)
    if not topic_list:
        topic_list = generate_topic_list(resume=state.get("resume"))
        logger.info(f"Initial Topic Result: {topic_list}")

    # all topic have answer
    if topic_idx >= len(topic_list) - 1:
        logger.info(f"Finished!")
        logger.debug(f"Final Topic Result: {topic_list}")
        logger.info(f"{generate_report(topic_list=topic_list)}")
        return Command(
            goto="_end__"
        )
    
    topic = topic_list[topic_idx]
    go_to_next = True
    for question in topic.questions:
        if not question.answered and question.iterations <= configurable.max_analyst_iterations:
            go_to_next = False
    
    if go_to_next:
        topic_idx += 1
        topic = topic_list[topic_idx]

        # all topic have answer
    if topic_idx >= len(topic_list) - 1:
        logger.info(f"Finished!")
        logger.debug(f"Final Topic Result: {topic_list}")
        logger.info(f"{generate_report(topic_list=topic_list)}")
        return Command(
            goto="_end__"
        )

    if not topic.background_investigation.searched:
        return Command(
            goto="background_investigator",
            update={
                "topic_list": topic_list,
                "topic_idx": topic_idx
            }
        )
    
    return Command(
        goto="analyst",
        update={
            "topic_list": topic_list,
            "topic_idx": topic_idx
        }
    )

def background_investigator_node(state: State) -> Command[Literal["analyst"]]:
    topic_list = state.get("topic_list")
    topic_idx = state.get("topic_idx")

    if topic_idx >= len(topic_list) - 1:
        logger.warning("return exception in background_investigator_node")
        return Command(
            goto="_end__"
        )
    
    topic = topic_list[topic_idx]
    query = topic.background_investigation.background_search_description
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY:
        searched_content = LoggedTavilySearch(max_results=SEARCH_MAX_RESULTS, include_images=False, include_image_descriptions=False).invoke(
            {"query":query}
        )
        investigation_results = None
        if isinstance(searched_content, list):
            investigation_results = [
                {"title": elem["title"], "content": elem["content"]}
                for elem in searched_content
            ]
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"
            )
    else:
        investigation_results = web_search_tool.invoke(query)

    background_investigation_context = [
        elem["content"]
        for elem in investigation_results 
    ]
    topic.background_investigation.searched = True
    topic.background_investigation.background_investigation_context = background_investigation_context
    topic_list[topic_idx] = topic
    return Command(
        update={
            "topic_list": topic_list,
        },
        goto="coordinator",
    )

def analyst_node(state: State, config: RunnableConfig) -> Command[Literal["coordinator", "researcher"]]:
    topic_list = state.get("topic_list")
    topic_idx = state.get("topic_idx")
    configurable = Configuration.from_runnable_config(config)

    if topic_idx >= len(topic_list) - 1:
        logger.warning("return exception in analyst_node")
        return Command(
            goto="_end__"
        )

    topic = topic_list[topic_idx]
    for question_idx, question in enumerate(topic.questions):
        if not question.answered and question.iterations <= configurable.max_analyst_iterations:
            break

    messages = apply_prompt_template("analyst", state)

    for context in topic.background_investigation.background_investigation_context:
        messages += [
            {
                "role": "user",
                "content": (
                    "Below are some background investigations for the user query question:\n"
                    + "\n".join(context)
                    + "\n"
                ),
            }
        ]


    for observation in question.observations:
        messages += [
            {
                "role": "user",
                "content": (
                    "Below are some observations for the user query question:\n"
                    + "\n".join(observation)
                    + "\n"
                ),
            }
        ]

    messages += [
        {
            "role": "user",
            "content": (
                "user query question is:\n"
                + question.description
                + "\n"
            ),
        }
    ]

    if AGENT_LLM_MAP["analyst"] == "basic":
        llm = get_llm_by_type(AGENT_LLM_MAP["analyst"]).with_structured_output(
            Report,
            method="json_mode",
        )
    else:
        llm = get_llm_by_type(AGENT_LLM_MAP["analyst"])
    
    full_response = ""
    if AGENT_LLM_MAP["analyst"] == "basic":
        response = llm.invoke(messages)
        full_response = response.model_dump_json(indent=4, exclude_none=True)
    else:
        response = llm.stream(messages)
        for chunk in response:
            full_response += chunk.content

    try:
        full_response = repair_json_output(full_response)
        report_json = json.loads(full_response)
    except json.JSONDecodeError:
        logger.warning("report response is not a valid JSON")
        return Command(goto="__end__")
    
    report = Report.model_validate(report_json)
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Report response: {report}")

    question.report = report
    if report.has_enough_context:
        question.answered = True

    topic.questions[question_idx] = question
    topic_list[topic_idx] = topic

    if question.answered:
        return Command(
            update={
                "topic_list": topic_list,
            },
            goto="coordinator"
        )

    return Command(
        update={
            "topic_list": topic_list,
        },
        goto="researcher"
    )

async def researcher_node(state: State, config: RunnableConfig) -> Command[Literal["coordinator", "analyst"]]:
    topic_list = state.get("topic_list")
    topic_idx = state.get("topic_idx")
    configurable = Configuration.from_runnable_config(config)

    if topic_idx >= len(topic_list) - 1:
        logger.warning("return exception in researcher_node")
        return Command(
            goto="_end__"
        )

    topic = topic_list[topic_idx]
    for question_idx, question in enumerate(topic.questions):
        if not question.answered and question.iterations <= configurable.max_analyst_iterations:
            break
    
    observations = []
    for step in question.report.steps:
        if step.need_web_search:
            agent_input = {
                "messages": [
                    HumanMessage(
                        content=f"#Task\n\n##title\n\n{step.title}\n\n##description\n\n{step.description}\n\n##locale\n\n{state.get('locale', 'zh-CN')}"
                    ),
                    HumanMessage(
                        content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                        name="system",
                    )
                ]
            }

            result = await research_agent.ainvoke(agent_input)
            response_content = result["messages"][-1].content
            logger.info(f"Step '{step.title}' execution completed:\n{response_content}")
            observations.append(response_content)

    question.iterations += 1
    question.observations = observations
    topic.questions[question_idx] = question
    topic_list[topic_idx] = topic

    if question.iterations > configurable.max_analyst_iterations:
        topic_idx += 1
        logger.info(f"Exceed maximum iterations:\n '{step.title}' \n{response_content}")
        return Command(
            update={
                "topic_list": topic_list,
                "topic_idx": topic_idx
            },
            goto="coordinator"
        )

    return Command(
        update={
            "topic_list": topic_list,
        },
        goto="analyst"
    )