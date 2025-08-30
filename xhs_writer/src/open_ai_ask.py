from openai import OpenAI
import asyncio
import os
from typing import List
from dotenv import load_dotenv
from prompt.example import FOODIE_ADVENTURE_1_PROMPT, FOODIE_ADVENTURE_2_PROMPT, FOODIE_ADVENTURE_3_PROMPT, THEME_1_PROMPT, THEME_2_PROMPT, THEME_3_PROMPT, TRAVEL_1_PROMPT, TRAVEL_2_PROMPT, TRAVEL_3_PROMPT, FASHION_1_PROMPT, FASHION_2_PROMPT, FASHION_3_PROMPT
from prompt.system import SYSTEM_PROMPT, TEMPLATE_PROMPT

load_dotenv()

class DeepSeekClient:
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def ask(self, content) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT,
                },
                {
                    'role': 'user',
                    'content': content,
                }
            ],
            model=self.model,
            temperature=1.5,  # 可以根据需要调整温度值，决定生成的随机性程度
        )
        if hasattr(chat_completion.choices[0].message, 'reasoning_content'):
            print('\n==========================================\n')
            print("推理的过程：\n")
            print(chat_completion.choices[0].message.reasoning_content)
        print('\n==========================================\n')
        print("生成的帖子：\n")
        print(chat_completion.choices[0].message.content)

class PromptChooser:
    def __init__(self, options: List[str]):
        self.options = options
        self.choice = 0
    def makeQuestion(self) -> str:
        res = '\n请选择：\n'
        for idx, op in enumerate(self.options):
            res += '\n==========================================\n'
            res += '{}.\n'.format(idx + 1)
            res += op
        res += '\n==========================================\n'
        res += '\n您的请选择是：'
        return res
    def makeChoice(self):
        try:
            decision = input(self.makeQuestion())
            if not decision.strip():
                print("没有有效选择，使用默认！\n")
                return
            choice = int(decision) - 1
            if choice >= len(self.options):
                print("没有有效选择，使用默认！\n")
                return
            self.choice = choice
        except:
            print("输入出现异常！\n")
    def makePrompt(self) -> str:
        return self.options[self.choice]

async def main():
    client = DeepSeekClient(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_API_KEY'),
        model=os.getenv('OPENAI_MODEL')
    )
    main_theme_choice = PromptChooser([THEME_1_PROMPT, THEME_2_PROMPT, THEME_3_PROMPT])
    main_theme_choice.makeChoice()

    example_choices = [PromptChooser([FOODIE_ADVENTURE_1_PROMPT, FOODIE_ADVENTURE_2_PROMPT, FOODIE_ADVENTURE_3_PROMPT]), PromptChooser([TRAVEL_1_PROMPT, TRAVEL_2_PROMPT, TRAVEL_3_PROMPT]), PromptChooser([FASHION_1_PROMPT, FASHION_2_PROMPT, FASHION_3_PROMPT])]
    
    example_choice = example_choices[main_theme_choice.choice]
    example_choice.makeChoice()

    keywords = input("\n请输入想要生成帖子的关键词：")
    if not keywords.strip():
        print("没有有效关键词！\n")
        return

    content = TEMPLATE_PROMPT.format(example = example_choice.makePrompt(), theme = main_theme_choice.makePrompt(), keywords = keywords)
    client.ask(content)

if __name__ == "__main__":
    asyncio.run(main())
