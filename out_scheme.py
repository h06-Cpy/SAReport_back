from typing import List

from pydantic import BaseModel
from datetime import date


class SentDistModel(BaseModel):
    name: str
    value: int


class TopicProportionModel(BaseModel):
    date: date
    topic0: float
    topic1: float
    topic2: float
    topic3: float
    topic4: float
    topic5: float
    topic6: float
    topic7: float
    topic8: float
    topic9: float

class TopicValueFloat(BaseModel):
    topic_name: str
    value: float


class TopicValueInt(BaseModel):
    topic_name: str
    value: int



class TotalTopicModel(BaseModel):
    tweet_number: int
    sentiment_dist: List[SentDistModel]
    sentiment_dist_rank: List[TopicValueInt]
    corr_rank_list: List[TopicValueFloat]
    topic_proportions: List[TopicProportionModel]



class CorrelationModel(BaseModel):
    window_sizes: List[int]
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
    max_corr_window_size: int
    correlations: CorrelationModel
    sentiment_corr: List[CorrLineModel]
    sentiment_dist: List[SentDistModel]
    topic_words: List[TopicWordModel]
    positive_words: List[SentKeywordModel]
    negative_words: List[SentKeywordModel]
    most_positive_day: str
    most_negative_day: str
    max_proportion_day: str
    min_proportion_day: str


class ReportDataModel(BaseModel):
    total_topic: TotalTopicModel
    topics: List[TopicModel]
