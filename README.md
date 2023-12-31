# chatNews

# 实现功能
本项目实现了一个类似 NewBing 的新闻检索系统, 可以从多个新闻源中根据用户的关键词检索新闻, 根据用户给出的问题, 检索出来答案.

# 流程
1. 使用Bert预训练模型对新闻进行关键词提取
2. 从news api中获取新闻
3. 从gnews api中获取新闻
4. 融合新闻源, 过滤新闻源的重复新闻, 使用openai chatgpt结合以思维链 prompt 的方式, 智能过滤
5. 对剩下新闻进行精排, 使用openai chatgpt结合以思维链 prompt 的方式, 智能重排, 选出最贴切问题的三个新闻
6. 对三个新闻使用爬虫爬取新闻全文, 使用 openai 压缩模型对新闻进行压缩, 生成摘要
7. 结合三个新闻的摘要, 使用 openai chatgpt 结合以 in-context-learning prompt 的方式, 智能生成答案

```mermaid
graph LR
A[用户输入问题] --> B[关键词提取]
B --> C[新闻源获取新闻]
C --> D[新闻源过滤]
D --> E[新闻源精排]
E --> F[新闻全文获取]
F --> G[新闻摘要生成]
G --> H[答案生成]
H --> I[答案返回]
```

# 运行结果
## 输入问题
`What are the protests in France about?`

## 结果输出
```
Protests in France are currently taking place in response to a new bill that grants police access to suspects' cameras, microphones, and GPS on their devices. The bill has been criticized as a "snoopers" charter, allowing unrestricted access to citizens' locations. Protests have also erupted over the death of teenager Nahel Merzouk, who was shot by a police officer. The demonstrations have resulted in clashes between protesters and police. The bill coincides with the expansion of police authority to monitor civilians using drones. President Macron argues that the bill is necessary to protect police officers from violent protesters. In response to the protests, Macron has threatened to shut down social media platforms used by protesters to film, post, and organize.From: Gizmodo Australia https://www.gizmodo.com.au/2023/07/france-passes-new-bill-allowing-police-to-remotely-activate-cameras-on-citizens-phones/
```

翻译:
```
目前在法国正在发生抗议活动，这是对一项新法案的回应，该法案授予警察访问嫌疑人手机摄像头、麦克风和GPS的权限。该法案被批评为“窥探者特权法案”，允许对公民的位置进行无限制的访问。此外，人们还对青少年纳赫尔·默尔祖克被警察射杀一事发起了抗议活动。这些示威活动导致抗议者和警察之间发生冲突。这项法案与扩大警方使用无人机监视民众的权力同时实施。马克龙总统辩称，该法案对保护警察免受暴力抗议者的袭击是必要的。作为对抗议活动的回应，马克龙威胁要关闭抗议者用于拍摄、发布和组织的社交媒体平台。来源：Gizmodo澳大利亚网站 https://www.gizmodo.com.au/2023/07/france-passes-new-bill-allowing-police-to-remotely-activate-cameras-on-citizens-phones/
```

## 思维链中间结果
去重
```json
"thoughts": {
    "reasoning": "The articles with UUIDs 76bccb7a-ff1c-4219-a62d-dba2e3ffc6b4 and 565202a2-b2a2-4f81-a5eb-22a0ecfc38b3 have the exact same title, description, URL, and source. The articles with UUIDs 726788b2-17cb-4a2b-9caa-c0839cb110c1 and 7904b6f2-2874-408a-b731-2c056250686c also have the exact same title, description, URL, and source. The articles with UUIDs 41b91f70-f927-409e-8d5f-fc5eb1f549bf and 5fd324e2-4b64-467f-a1fa-70db13ae898a have different titles and descriptions but are from the same source and have similar content.",
}
```

精排
```json
"thoughts": {
    "reasoning": "The most relevant articles will provide information specifically about the protests in France. The first article from RTE.ie explicitly mentions protests against police violence in France. The second article from Gizmodo Australia mentions ongoing protests in France. The third article from The Indian Express talks about violent clashes between police and protesters in France. Based on this reasoning, the three most relevant articles are: 565202a2-b2a2-4f81-a5eb-22a0ecfc38b3, 7904b6f2-2874-408a-b731-2c056250686c, 5fd324e2-4b64-467f-a1fa-70db13ae898a."
}
```

# 使用技术

## 使用Bert预训练模型
使用sentence-transformers模型, 提取关键词

## 使用langchain调用GPT模型
使用langchain, 使链式调用GPT模型更加简单

## 使用 playwright 爬取新闻全文
使用 playwright 爬取新闻全文, 反爬虫能力强


# 难点及解决方案

## 难点
1. 如何避免 AI 幻觉现象
在我们的代码中, 我们使用in-context-learning的方法希望ai对齐我们的输入, 例如, 输出一个json作为我们的思维链的载体, 方便我们解析.

在某些情况, ai 会输出不合格的 json, 例如带上了末尾的逗号, 或者缺少了引号, 这些都会导致我们的思维链无法解析, 从而导致思维链无法继续进行.

我们的解决方案是, 首先在代码层面兼容ai的输出, 我们使用json5来解析json, 从而兼容ai的输出. 另外, 我们使用了retry装饰器来重试ai的输出, 从而避免了ai输出不能解析的json.

2. 如何避免浏览器内容过于丰富, ai 难以捉到关键信息
浏览网页时, 会有很多广告, 链接等无关信息, 这些信息会干扰ai的判断, 从而导致ai无法捉到关键信息. 

我们提出的解决方案是, 使用 firefox 的 reader view 模式, 可以将网页转化为纯文本, 过滤掉广告, 链接等无关页面元素, 方便ai模型处理






