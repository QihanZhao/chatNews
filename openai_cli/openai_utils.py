import asyncio
import json5
from typing import List

import tenacity
from langchain.schema import SystemMessage, HumanMessage
from langchain.text_splitter import CharacterTextSplitter

from utils.browse import abrowse_web_page_in_reader_mode
from models.model import News
from openai_cli.openai_client import get_completion, aget_completion, get_completion_with_context
from utils.logger import logger
from utils.retry import retry, async_retry



@retry(max_retries=3, initial_delay=0, multiplier=1)
def keywords_extraction(question: str) -> List[str]:
    system_instruct = '''Please acting as a news editor, extract the keywords from the following question. The keywords should be concise and accurate, which helps you to search the news.
You should only respond in JSON format as described below.
RESPONSE FORMAT:
{
    "thoughts": {
        "reasoning": "step-by-step reasoning in painstaking detail, tied to the original text",
    },
    "result": ["keyword1", "keyword2"]
}
Ensure the response can be parsed by Python json.loads'''
    result = get_completion(system_instruct, question, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613")
    return json5.loads(result)["result"]


@retry(max_retries=3, initial_delay=0, multiplier=1)
def filter_non_meaningful_keywords(keywords: str) -> List[str]:
    system_instruct = '''Please acting as a news editor, filter the non-meaningful keywords from the following keywords.
You should only respond in JSON format as described below.
RESPONSE FORMAT:
{
    "thoughts": {
        "reasoning": "step-by-step reasoning in painstaking detail, tied to the original text",
    },
    "result": ["keyword1", "keyword2"]
}
Ensure the response can be parsed by Python json.loads'''
    result = get_completion(system_instruct, keywords, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613")
    logger.info(f"{result=}")
    return json5.loads(result)["result"]


@retry(max_retries=3, initial_delay=0, multiplier=1)
def text_summarize(original_text: str) -> str:
    system_instruct = "Please acting as a news editor, summarize the following article given by the author. " \
                      "Attention: the summary should be concise and accurate, do not add any personal opinions and don't change the meaning of the original text."

    result = get_completion(system_instruct, original_text, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613")
    return result


@retry(max_retries=3, initial_delay=0, multiplier=1)
def text_summarize_with_question(original_text: str, question: str) -> str:
    system_instruct = "Please acting as a news editor, summarize the following article given by the author." \
                      "Attention: the summary should be concise and accurate, do not add any personal opinions and don't change the meaning of the original text." \
                      "The summarization should follow the guideline of the question. You are not supposed to answer the question but summarize the text about the questions." \
                      "The summarization should not exceed 200 words." \
                      "Question: \n" + question

    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    texts = text_splitter.split_text(original_text)

    tasks = []
    for text in texts:
        tasks.append(
            aget_completion(system_instruct, text, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613"))
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(asyncio.gather(*tasks))
    result = "".join(result)

    result = get_completion(system_instruct, result, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613")

    return result


@async_retry(max_retries=3, initial_delay=0, multiplier=1)
async def atext_summarize_with_question(original_text: str, question: str) -> str:
    system_instruct = "Please acting as a news editor, summarize the following article given by the author." \
                      "Attention: the summary should be concise and accurate, do not add any personal opinions and don't change the meaning of the original text." \
                      "The summarization should follow the guideline of the question. You are not supposed to answer the question but summarize the text about the questions." \
                      "The summarization should not exceed 200 words." \
                      "Question: \n" + question

    text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    texts = text_splitter.split_text(original_text)

    tasks = []
    for text in texts:
        tasks.append(
            aget_completion(system_instruct, text, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613"))
    result = await asyncio.gather(*tasks)
    result = "".join(result)

    result = await aget_completion(system_instruct, result, temperature=0.7, max_tokens=2 * 1024,
                                   model_name="gpt-3.5-turbo-0613")

    return result


async def asummary_news(news:News, question: str) -> str:
    logger.info("start summarizing news: " + news.title)
    content = await abrowse_web_page_in_reader_mode(news.url)
    result = await atext_summarize_with_question(content, question) + "From: " + news.source + " " + news.url
    logger.info("finish summarizing news: " + result)
    return result


@retry(max_retries=3, initial_delay=0, multiplier=1)
def filter_same_article(news: str) -> List[str]:
    system_instruct = \
        """Please acting as a news editor, there are some articles from different sources. Some of them are the same article. Please filter out the same articles and keep the unique ones.
        You can make the decision based on the title, description, and source of the article. You can also open the url to check the content of the article.
        You should only respond in JSON format as described below
        RESPONSE FORMAT:
        {
            "thoughts": {
                "reasoning": "step-by-step reasoning in painstaking detail, tied to the original text",
            }, 
            "result": [<uuid1>, <uuid2>, <uuid3>]
        }"""

    result = get_completion(system_instruct, news, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613")
    logger.info(result)
    return json5.loads(result)["result"]


@retry(max_retries=3, initial_delay=0, multiplier=1)
def news_ask_questions(news: str, question: str) -> str:
    system_instruct = "Please acting as a news editor, reply the question given about the following news summaries." \
                      "Attention: the question should be concise and accurate, do not add any personal opinions and don't change the meaning of the original text."
    example_question = "In which country google news search is restricted?"
    example_news = """
0 Google has announced that it will no longer allow Canadian users to search for news on its platform in response to Canada's Online News Act. The legislation would require internet companies to pay news publishers for accessing and reproducing their content. This move by Google follows Meta's decision to cut off Canadian users' access to news links on Facebook and Instagram in protest of the law. Supporters of the bill argue that it serves as digital reparations for struggling news outlets, while opponents, like Google, view it as an unnecessary "link tax." This clash between Big Tech and the Canadian government has put news organizations and internet users in the middle. Gizmodo Australia https://www.gizmodo.com.au/2023/06/google-says-it-would-rather-shut-off-canadian-news-links-than-pay-publishers/
1 Google has announced that it will remove Canadian news links from its search results and other products in response to Canada's Online News Act, which requires tech companies to pay news publishers for accessing their content. The move follows Meta's (formerly Facebook) decision to cut off Canadian users' access to news links in protest of the law. Supporters argue that the legislation provides compensation to news outlets affected by the shift to digital media, while opponents, including Google, see it as an unworkable "link tax." The situation has sparked a battle between Big Tech and the Canadian government, with news organizations and Canadian internet users caught in the middle. The proposed law has drawn criticism from Google, who claims it creates uncertainty and financial liability. It remains to be seen who will budge first in this standoff. Gizmodo Australia https://www.gizmodo.com.au/2023/06/google-says-it-would-rather-shut-off-canadian-news-links-than-pay-publishers/
"""
    example_answer = "According to the information provided in the article from Gizmodo Australia, Google has announced that it will no longer allow Canadian users to search for news on its platform. Therefore, the country where Google news search is currently restricted is Canada."
    context = [
        SystemMessage(content=system_instruct),
        HumanMessage(content=f"News: {example_news} Question: {example_question}", example=True),
        SystemMessage(content=example_answer)
    ]
    result = get_completion_with_context(context, f"News: {news} Question: {question}", temperature=0.7,
                                         max_tokens=2 * 1024,
                                         model_name="gpt-3.5-turbo-0613")

    return result


@retry(max_retries=3, initial_delay=0, multiplier=1)
def fine_ranking(news: str, question: str) -> List[str]:
    system_instruct = '''Please acting as a news editor, rank the following articles. The ranking should be based on the relevance of the article to the question. 
The most relevant article should be ranked first. You should find out 3 most relevant articles. 
You should only respond in JSON format as described below.
RESPONSE FORMAT:
{
    "thoughts": {
        "reasoning": "step-by-step reasoning in painstaking detail, tied to the original text",
    },
    "result": ["<uuid1>", "<uuid2>", "<uuid3>"]
}
Ensure the response can be parsed by Python json.loads'''

    message = "Question: \n" + question + "\n" + "Articles: \n" + news
    result = get_completion(system_instruct, message, temperature=0.7, max_tokens=2 * 1024,
                            model_name="gpt-3.5-turbo-0613")
    logger.info(result)
    return json5.loads(result)["result"]


if __name__ == '__main__':
    text = """
    Protests have erupted in France over the death of a 17-year-old teenager, Nahel, who was killed by a French police officer during a traffic stop in Nanterre, a suburb of Paris. The protests have resulted in clashes between the police and the youth, with reports of burnt cars and broken glass panes. French President Emmanuel Macron has attended a government emergency meeting in response to the riots.France is currently experiencing widespread protests. The specific cause of the protests is not mentioned in the article.In France, people are protesting against the fatal police shooting of a 17-year-old driver in the Paris suburb of Nanterre. The protests have led to clashes between protesters and police, resulting in burnt vehicles and buildings.Protesters in France are demonstrating against police violence and demanding justice following the death of a 17-year-old teenager named Nahel, who was killed by a police officer during a traffic stop. The protests have resulted in clashes between protesters and police, with reports of vandalism and burned buildings.Protests are taking place across France following the deadly police shooting of a teenager. The protests, which have now entered their fourth day, have seen clashes between young rioters and the police, as well as looting of stores. President Emmanuel Macron has appealed to parents to keep their children off the streets and has blamed social media for exacerbating the unrest. The protests have spread to cities such as Strasbourg, Marseille, and Lyon, with incidents of violence and looting reported. In Marseille, looters even broke into a gun shop and made off with weapons.French people are protesting against the deadly police shooting of a teenager of Algerian and Moroccan descent during a traffic stop. The protests have escalated into riots in major cities and overseas territories, leading to hundreds of arrests and violence. President Emmanuel Macron has not declared a state of emergency but has increased law enforcement response, deploying an additional 5,000 officers. The Interior Minister has ordered a nighttime shutdown of public buses and trams and warned social networks against being used for calls to violence.People in France are protesting against police violence and the proposed security law that would limit the ability to film and share images of police officers. The protests were sparked by the recent police beating of a Black man, which was captured on video and circulated on social media. The government has responded by promising to crack down on those who incite violence on social media platforms, and calling for the removal of sensitive content. President Macron has also called on parents to keep their children at home to prevent further unrest.The people in France are protesting against the shooting and killing of a teenager by a police officer in the Paris suburb of Nanterre. The protests have resulted in riots, barricades, fires, and clashes with the police. The officer has been charged with voluntary homicide, and the unrest raises concerns as Paris is set to host the Olympic Games in 2024. The protests have spread to other towns and cities in France and even to Brussels in Belgium.The people in France are protesting against police violence and demanding more accountability. The recent death of a 10-year-old boy named Nahel, who was shot by a police officer, has sparked outrage and calls for justice. The protests are also fueled by ongoing issues of racial injustice and inequality in disadvantaged neighborhoods.Protests in France are being held in response to the killing of a 17-year-old by police in the Paris suburb of Nanterre. Anti-racism activists are also highlighting concerns about police behavior in general. These protests echo similar demonstrations in 2005 following the deaths of two teenagers who were electrocuted while hiding from police.
    """

    question = "Why are people protesting in France?"
    logger.info(news_ask_questions(text, question))
