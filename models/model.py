import uuid
from enum import Enum

from pydantic import BaseModel


class TypeKeywordsPreprocessMethod(str, Enum):
    BERT = "BERT"
    CHATGPT = "CHATGPT"
    MIXED = "MIXED"


class News(BaseModel):
    title: str
    description: str
    url: str
    full_article: str | None
    source: str
    published_at: str
    uuid: str | None

    def __init__(self, **data):
        super().__init__(**data)
        self.uuid = str(uuid.uuid4())

    def __str__(self):
        return f"Title: {self.title}\n" \
               f"Description: {self.description}\n" \
               f"URL: {self.url}\n" \
               f"Source: {self.source}\n" \
               f"Published at: {self.published_at}\n"\
                  f"UUID: {self.uuid}"


    def __eq__(self, other):
        return self.uuid == other.uuid
