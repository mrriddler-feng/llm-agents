import logging
from dataclasses import dataclass, field
from typing import Annotated, Optional

import yaml
from dotenv import load_dotenv
from pydantic import Field

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import cartesia, deepgram, openai, silero

# from livekit.plugins import noise_cancellation

from src.prompts.questions import INTERVIEWER_PROMPT, QUESTION_PROMPT, QUESTION_PROMPT_STR

logger = logging.getLogger("expert-interview")
logger.setLevel(logging.INFO)

load_dotenv()

voices = {
    "greeter": "794f9389-aac1-45b6-b726-9d9369183238",
    "reservation": "156fb8d2-335b-4950-9cb3-a2d33befec77",
    "takeaway": "6f84f4b8-58a2-430c-8c79-688dad597532",
    "checkout": "39b376fc-488e-4d0c-8b37-e00b72059fdd",
}


@dataclass
class UserData:
    interviewee_name: Optional[str] = None
    interviewee_phone: Optional[str] = None

    answers: dict[str, str] = field(default_factory=dict)
    agents: dict[str, Agent] = field(default_factory=dict)

    def summarize(self) -> str:
        data = {
            "interviewee_name": self.interviewee_name or "unknown",
            "interviewee_phone": self.interviewee_phone or "unknown",
        }
        # summarize in yaml performs better than json
        return yaml.dump(data)


RunContext_T = RunContext[UserData]

class BaseAgent(Agent):
    async def on_enter(self) -> None:
        agent_name = self.__class__.__name__
        logger.info(f"entering task {agent_name}")

        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()

        # add an instructions including the user data as assistant message
        chat_ctx.add_message(
            role="system",  # role=system works for OpenAI's LLM and Realtime API
            content=f"Current user data is {userdata.summarize()}",
        )
        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply(tool_choice="none")
    
    async def on_exit(self) -> None:
        userdata: UserData = self.session.userdata
        res = ["===================================="]
        for idx, question in enumerate(QUESTION_PROMPT):
            answerIdx = str(idx + 1)
            if answerIdx in userdata.answers:
                line = ""
                if idx > 0:
                    line += "\n"
                line += "Q:"
                line += question
                line += "\nA:"
                line += userdata.answers[answerIdx]
                res.append(line)
        res += ["===================================="]
        print("\n".join(res))


@function_tool()
def update_answer(
        question_num: Annotated[str, Field(description="Question number from the question list")],
        answer: Annotated[str, Field(description="The answer to the question")],
        context: RunContext_T,
    ) -> str:
        """Called when the interviewee answers the questions in question list."""
        userdata = context.userdata
        userdata.answers[question_num] = answer
        logger.info(f"recieve question answer {answer}")
        return f"The answer to question: {answer}"
    
class Interviewer(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                INTERVIEWER_PROMPT.format(questions_str=QUESTION_PROMPT_STR)
            ),
            tools=[],
            tts=cartesia.TTS(voice=voices["checkout"]),
        )

    @function_tool()
    async def update_one_answer(
        self,
        answer: Annotated[str, Field(description="The interviewee input content to the question")],
        context: RunContext_T,
    ) -> str:
        update_answer("1", answer, context)
        """Called when the interviewee answers the no.1 question in question list."""
        return f"The answer to question: {answer}"
    
    @function_tool()
    async def update_two_answer(
        self,
        answer: Annotated[str, Field(description="The interviewee input content to the question")],
        context: RunContext_T,
    ) -> str:
        update_answer("2", answer, context)
        """Called when the interviewee answered the no.2 question in question list."""
        return f"The answer to question: {answer}"
    
    @function_tool()
    async def update_three_answer(
        self,
        answer: Annotated[str, Field(description="The interviewee input content to the question")],
        context: RunContext_T,
    ) -> str:
        update_answer("3", answer, context)
        """Called when the interviewee answered the no.3 question in question list."""
        return f"The answer to question: {answer}"
    
    @function_tool()
    async def update_four_answer(
        self,
        answer: Annotated[str, Field(description="The interviewee input content to the question")],
        context: RunContext_T,
    ) -> str:
        update_answer("4", answer, context)
        """Called when the interviewee answered the no.4 question in question list."""
        return f"The answer to question: {answer}"
    
    @function_tool()
    async def update_five_answer(
        self,
        answer: Annotated[str, Field(description="The interviewee input content to the question")],
        context: RunContext_T,
    ) -> str:
        update_answer("5", answer, context)
        """Called when the interviewee answered the no.5 question in question list."""
        return f"The answer to question: {answer}"

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    userdata = UserData()
    userdata.agents.update(
        {
            "interviewer": Interviewer(),
        }
    )
    session = AgentSession[UserData](
        userdata=userdata,
        stt=deepgram.STT(language="zh-CN", model="nova-2"),
        llm=openai.LLM.with_deepseek(),
        tts=cartesia.TTS(language="zh-CN"),
        vad=silero.VAD.load(),
        max_tool_steps=5,
        # to use realtime model, replace the stt, llm, tts and vad with the following
        # llm=openai.realtime.RealtimeModel(voice="alloy"),
    )

    await session.start(
        agent=userdata.agents["interviewer"],
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # await agent.say("Welcome to our restaurant! How may I assist you today?")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
