from datetime import date

import pandas as pd

from database import Session
from models import DailyTopicProportion, Topic, DailyIndex, DailySentScore
from out_scheme import ReportDataModel, SentDistModel, TopicProportionModel, TotalTopicModel, CorrelationModel, \
    CorrLineModel, TopicWordModel, SentKeywordModel, TopicModel

datelist = [stamp.date() for stamp in pd.date_range(date(2023, 5, 23), date(2023, 6, 8))]


def get_report_data_model(session: Session):
    # total_topic 만들기
    total_topic = session.get(Topic, 11)
    topic_proportions = []
    for day in datelist:
        topic_proportions.append(get_topic_proportion_model(day, session))
    total_topic_model = TotalTopicModel(sentiment_dist=get_sent_dist_models(total_topic),
                                        topic_proportions=topic_proportions,
                                        tweet_number=total_topic.tweet_number)

    # topics 만들기
    topics = []
    for i in range(1, 11):
        topics.append(get_topic_model(i, session))

    return ReportDataModel(total_topic=total_topic_model, topics=topics)


def get_sent_dist_models(topic: Topic):
    sd_list = []
    sd = topic.sent_dist[0]
    sd_list.append(SentDistModel(name='긍정', value=sd.pos_percent))
    sd_list.append(SentDistModel(name='부정', value=sd.neg_percent))
    sd_list.append(SentDistModel(name='중립', value=sd.neutral_percent))
    return sd_list


def get_topic_proportion_model(day, session):
    proportions = []
    dtps = session.query(DailyTopicProportion).where(DailyTopicProportion.date == day).all()
    for i in range(10):
        proportions.append(dtps[i].proportion)
    return TopicProportionModel(date=day, topic1=round(proportions[0], 3),
                                topic2=round(proportions[1], 3),
                                topic3=round(proportions[2], 3),
                                topic4=round(proportions[3], 3),
                                topic5=round(proportions[4], 3),
                                topic6=round(proportions[5], 3),
                                topic7=round(proportions[6], 3),
                                topic8=round(proportions[7], 3),
                                topic9=round(proportions[8], 3),
                                topic10=round(proportions[9], 3),
                                )


def get_topic_model(topic_number, session):
    topic = session.get(Topic, topic_number)
    topic_name = topic.topic_name
    tweet_number = topic.tweet_number
    sentiment_dist = get_sent_dist_models(topic)
    correlations = get_corr_model(topic)
    sentiment_corr = []
    for day in datelist:
        sentiment_corr.append(get_corrline_model(day, topic_number, session))
    topic_words = []
    for topic_word in topic.topic_words[:30]:
        topic_words.append(TopicWordModel(text=topic_word.word, value=topic_word.value))

    positive_words = []
    negative_words = []
    for sk in topic.sent_keywords:
        if sk.value > 0:
            positive_words.append(SentKeywordModel(name=sk.keyword, value=sk.value))
        else:
            negative_words.append(SentKeywordModel(name=sk.keyword, value=abs(sk.value)))

    return TopicModel(topic_name=topic_name, correlations=correlations,
                      sentiment_dist=sentiment_dist, sentiment_corr=sentiment_corr,
                      topic_words=topic_words, positive_words=positive_words,
                      negative_words=negative_words, tweet_number=tweet_number)


def get_corrline_model(day: date, topic_number, session):
    index = session.query(DailyIndex).where(DailyIndex.date == day).one()
    sentiment = session.query(DailySentScore).where(DailySentScore.topic_id == topic_number,
                                                    DailySentScore.date == day).one()
    return CorrLineModel(date=day, sentiment=round(sentiment.sent_score, 3),
                         snp500=round(index.snp500, 3), nasdaq100=round(index.nasdaq100, 3))


def get_corr_model(topic: Topic):
    refer_days = []
    snp500 = []
    nasdaq100 = []
    for correlation in topic.correlations:
        refer_days.append(correlation.refer_day)
        snp500.append(round(correlation.snp500_corr,3))
        nasdaq100.append(round(correlation.nasdaq100_corr,3))

    return CorrelationModel(refer_days=refer_days, snp500=snp500, nasdaq100=nasdaq100)
