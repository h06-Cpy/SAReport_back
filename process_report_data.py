from datetime import date

import pandas as pd

from database import get_db, Session
from models import SentDist, DailyTopicProportion, Topic, DailyIndex, DailySentScore
from out_scheme import ReportDataModel, SentDistModel, TopicProportionModel, TotalTopicModel, CorrelationModel, \
    CorrLineModel, TopicWordModel, SentKeywordModel, TopicModel

datelist = [stamp.date() for stamp in pd.date_range(date(2023, 5, 23), date(2023, 6, 8))]

def get_report_data_model(session: Session):

    # total_topic 만들기
    topic_proportions = []
    for day in datelist:
        topic_proportions.append(get_topic_proportion_model(day, session))
    total_topic = TotalTopicModel(sentiment_dist=get_sent_dist_models(11, session),
                                  topic_proportions=topic_proportions)

    # topics 만들기
    topics = []
    for i in range(1,11):
        topics.append(get_topic_model(i, session))

    return ReportDataModel(total_topic=total_topic, topics=topics)

def get_sent_dist_models(topic_number, session):
    sd_list = []
    sd = session.query(SentDist).where(SentDist.topic_id==topic_number).one()
    sd_list.append(SentDistModel(name='긍정', value=sd.pos_percent))
    sd_list.append(SentDistModel(name='부정', value=sd.neg_percent))
    sd_list.append(SentDistModel(name='중립', value=sd.neutral_percent))
    return sd_list

def get_topic_proportion_model(day, session):
    proportions = []
    dtps = session.query(DailyTopicProportion).where(DailyTopicProportion.date == day).all()
    for i in range(10):
        proportions.append(dtps[i].proportion)
    return TopicProportionModel(date=day, topic1=proportions[0],
                                topic2=proportions[1],
                                topic3=proportions[2],
                                topic4=proportions[3],
                                topic5=proportions[4],
                                topic6=proportions[5],
                                topic7=proportions[6],
                                topic8=proportions[7],
                                topic9=proportions[8],
                                topic10=proportions[9],
                                )

def get_topic_model(topic_number, session):
    topic = session.get(Topic, topic_number)
    topic_name = topic.topic_name
    sentiment_dist = get_sent_dist_models(topic_number, session)
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
        if sk.value>0:
            positive_words.append(SentKeywordModel(name=sk.keyword, value=sk.value))
        else:
            negative_words.append(SentKeywordModel(name=sk.keyword, value=abs(sk.value)))

    return TopicModel(topic_name=topic_name,correlations=correlations,
                      sentiment_dist=sentiment_dist,sentiment_corr=sentiment_corr,
                      topic_words=topic_words, positive_words=positive_words,
                      negative_words=negative_words)

def get_corrline_model(day:date, topic_number, session):
    index = session.query(DailyIndex).where(DailyIndex.date==day).one()
    sentiment = session.query(DailySentScore).where(DailySentScore.topic_id==topic_number,
                                                    DailySentScore.date==day).one()
    return CorrLineModel(date=day, sentiment=sentiment.sent_score,
                         snp500=index.snp500, nasdaq100=index.nasdaq100)

def get_corr_model(topic: Topic):
    refer_days = []
    snp500 = []
    nasdaq100 = []
    for correlation in topic.correlations:
        refer_days.append(correlation.refer_day)
        snp500.append(correlation.snp500_corr)
        nasdaq100.append(correlation.nasdaq100_corr)

    return CorrelationModel(refer_days=refer_days, snp500=snp500, nasdaq100=nasdaq100)