from typing import List

from pydantic import BaseModel
from datetime import date


class SentDistModel(BaseModel):
    name: str
    value: int


class TopicProportionModel(BaseModel):
    date: date
    topic1: float
    topic2: float
    topic3: float
    topic4: float
    topic5: float
    topic6: float
    topic7: float
    topic8: float
    topic9: float
    topic10: float


class TotalTopicModel(BaseModel):
    sentiment_dist: List[SentDistModel]
    topic_proportions: List[TopicProportionModel]
    tweet_number: int


class CorrelationModel(BaseModel):
    refer_days: List[int]
    snp500: List[float]
    nasdaq100: List[float]


class CorrLineModel(BaseModel):
    date: date
    sentiment: float
    snp500: float
    nasdaq100: float


class TopicWordModel(BaseModel):
    text: str
    value: int


class SentKeywordModel(BaseModel):
    name: str
    value: float


class TopicModel(BaseModel):
    topic_name: str
    tweet_number: int
    correlations: CorrelationModel
    sentiment_corr: List[CorrLineModel]
    sentiment_dist: List[SentDistModel]
    topic_words: List[TopicWordModel]
    positive_words: List[SentKeywordModel]
    negative_words: List[SentKeywordModel]


class ReportDataModel(BaseModel):
    total_topic: TotalTopicModel
    topics: List[TopicModel]
