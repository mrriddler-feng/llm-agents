# 概念

这是一个简历背调工具，通过LLM汇总信息、搜索完成的概念证明工程，可以直接用CLI操作。

## 样例

输入：
example简历文件。
输出：

## 安装

```
uv sync

cp exapmles/.env.example .env

cp exapmles/conf.yaml.example conf.yaml

```
## 技术

工程基于[deer-flow](https://github.com/bytedance/deer-flow)建设，主要包含了Agent的Plan模式和Muti-Agent模式。主要包含：

1. reviewer：从简历中提取关键内容。
2. analyst：需要回答预设的关于候选人背景的问题，如果没有足够信息回答需要制定进一步进行搜索更多信息的计划。
3. researcher：对相关信息进一步检索。
   

