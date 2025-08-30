# 概念

这是一个专家访谈工具，通过LLM作为VoiceAgnet完成的概念证明工程，可以直接用CLI操作。

## 样例

输入：
>1.您目前就职于哪家公司？
>2.您目前做哪方面的业务？
>3.您所在的业务占主站的Dau贡献比例是多少？
>4.您所在的业务在主站下的主要目标是什么？
>5.您所在的业务今年的主要发力点是什么？

输出：
![demo](https://github.com/mrriddler-feng/llm-agents/blob/main/expert_interview/examples/expert_interview_demo.png)

## 安装

```
uv sync

cp exapmles/.env.example .env

```
## 技术

工程基于[livekit](https://github.com/livekit/agents)建设，主要包含了tts、ttt、stt(标准VoiceAgent Pipeline)。
   

