# 概念

这是一个小红书帖子生成器，通过LLM文生文完成的概念证明工程，可以直接用CLI操作。

## 样例

输入：
> 主题：南昌土著推荐，美食全攻略 店名：老地方好味坊 推荐菜：亮亮水煮、蟹脚捞粉、麻辣藕片、招牌啤酒鸭 推荐理由：平价好吃不踩雷 地址：江西省南昌市中山路万寿宫历史文化街区
输出：

## 安装

```
uv sync

cp exapmles/.env.example .env

```

## 技术

工程使用了[Few-Shot Prompting](https://www.promptingguide.ai/techniques/fewshot)[](https://www.promptingguide.ai/techniques/fewshot)技巧，通过把热门帖子作为样例，让LLM基于样例进行仿写。
