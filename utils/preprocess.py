from typing import List

from keybert import KeyBERT

from openai_cli import openai_utils
from utils.logger import logger

model = KeyBERT('distilbert-base-nli-mean-tokens')


def get_keywords_by_bert(query: str) -> List[str]:
    keywords = model.extract_keywords(query, keyphrase_ngram_range=(1, 2))
    logger.info(keywords)
    result = []
    for i in keywords:
        result.append(i[0])

    return result


def get_keywords_by_gpt3(query: str) -> List[str]:
    result = openai_utils.keywords_extraction(query)
    logger.info(result)
    return result


def get_keywords_by_mixed(query: str) -> List[str]:
    keywords = get_keywords_by_bert(query)
    keywords = openai_utils.filter_non_meaningful_keywords(str(keywords))
    return keywords
