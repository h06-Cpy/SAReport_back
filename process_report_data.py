from datetime import date

from sqlalchemy import text

from database import Session
from models import DailyTopicProportion, Topic, DailyIndex, DailySentScore
from out_scheme import ReportDataModel, SentDistModel, TopicProportionModel, TotalTopicModel, CorrelationModel, \
    CorrLineModel, TopicWordModel, SentKeywordModel, TopicModel, TopicValueInt, TopicValueFloat
from time_series_data import datelist


def get_report_data_model(session: Session):
    # total_topic 만들기
    all_topic_list = session.query(Topic).all()
    total_topic = all_topic_list[10]
    sentiment_dist_rank = get_sentiment_dist_rank(all_topic_list, session)
    corr_rank_list = get_corr_rank_list(all_topic_list, session)
    topic_proportions = []

    for day in datelist:
        tpm= get_topic_proportion_model_and_rank( day, session)
        topic_proportions.append(tpm)

    total_topic_model = TotalTopicModel(tweet_number=total_topic.tweet_number,
                                        sentiment_dist=get_sent_dist_models(total_topic),
                                        sentiment_dist_rank=sentiment_dist_rank,
                                        corr_rank_list=corr_rank_list,
                                        topic_proportions=topic_proportions,
                                        )

    # topics 만들기
    topics = []
    for i in range(1, 11):
        topics.append(get_topic_model(all_topic_list[i-1], session))

    return ReportDataModel(total_topic=total_topic_model, topics=topics)

def get_corr_rank_list(all_topic_list, session: Session):
    corr_rank_list = []
    result = []
    for i in range(1,11):
        sql = text(f'select avg(snp500_corr) from correlation where topic_id={i}')
        rows = session.execute(sql)
        avg_corr = next(rows)[0]
        corr_rank_list.append((i,avg_corr))
    corr_rank_list.sort(key=lambda x: x[1], reverse=False)
    for corr_rank in corr_rank_list:
        result.append(TopicValueFloat(topic_name=all_topic_list[corr_rank[0]-1].topic_name,
                                      value=round(corr_rank[1],3)))
    return result

def get_sentiment_dist_rank(all_topic_list, session:Session):
    sent_dist_rank = []
    sql = text('select topic_id, pos_percent - neg_percent from sent_dist where topic_id != 11 order by (pos_percent - neg_percent) desc ')
    rows = session.execute(sql)
    for row in rows:
        sent_dist_rank.append(TopicValueInt(topic_name=all_topic_list[row[0]-1].topic_name,
                                            value=row[1]))
    return sent_dist_rank


def get_sent_dist_models(topic: Topic):
    sd_list = []
    sd = topic.sent_dist[0]
    sd_list.append(SentDistModel(name='긍정', value=sd.pos_percent))
    sd_list.append(SentDistModel(name='부정', value=sd.neg_percent))
    sd_list.append(SentDistModel(name='중립', value=sd.neutral_percent))
    return sd_list


def get_topic_proportion_model_and_rank( day:date, session:Session):
    proportions = []
    dtps = session.query(DailyTopicProportion).where(DailyTopicProportion.date == day).all()
    for i in range(10):
        proportions.append(dtps[i].proportion)


    return TopicProportionModel(date=day, topic0=round(proportions[0], 3),
                                topic1=round(proportions[1], 3),
                                topic2=round(proportions[2], 3),
                                topic3=round(proportions[3], 3),
                                topic4=round(proportions[4], 3),
                                topic5=round(proportions[5], 3),
                                topic6=round(proportions[6], 3),
                                topic7=round(proportions[7], 3),
                                topic8=round(proportions[8], 3),
                                topic9=round(proportions[9], 3),
                                )


def get_max_min_sent_day(topic_id: int, max_corr_window_size, session: Session):
    result_dates = []
    sql = text(f'select date from daily_sent_score where topic_id={topic_id} and window_size={max_corr_window_size} order by sent_score desc')
    rows = session.execute(sql)
    for row in rows:
        result_dates.append(row[0])
    return result_dates[0], result_dates[-1]


def get_max_min_proportion_day(topic_id: int, session: Session):
    result_dates = []
    sql = text(f'select date from daily_topic_proportion where topic_id={topic_id} order by proportion desc')
    rows = session.execute(sql)
    for row in rows:
        result_dates.append(row[0])
    return result_dates[0], result_dates[-1]


def get_topic_model(topic, session):
    topic_name = topic.topic_name
    tweet_number = topic.tweet_number
    sentiment_dist = get_sent_dist_models(topic)
    correlations, max_corr_window_size = get_corr_model_and_max_window(topic)
    sentiment_corr = []
    for day in datelist[max_corr_window_size:]:
        sentiment_corr.append(get_corrline_model(day, topic.id, max_corr_window_size, session))
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

    most_positive_day, most_negative_day = get_max_min_sent_day(topic.id, max_corr_window_size, session)
    max_proportion_day, min_proportion_day = get_max_min_proportion_day(topic.id, session)

    return TopicModel(topic_name=topic_name, correlations=correlations,
                      sentiment_dist=sentiment_dist, sentiment_corr=sentiment_corr,
                      topic_words=topic_words, positive_words=positive_words,
                      negative_words=negative_words, tweet_number=tweet_number,
                      max_corr_window_size=max_corr_window_size,
                      most_positive_day=most_positive_day,
                      most_negative_day=most_negative_day,
                      max_proportion_day=max_proportion_day,
                      min_proportion_day=min_proportion_day)


def get_corrline_model(day: date, topic_id: int, max_corr_window_size: int, session: Session): # 여기를 이제 상관관계 가장 높은 window 사이즈 골라서 보내기
    index = session.query(DailyIndex)\
        .where(DailyIndex.date == day, DailyIndex.window_size==max_corr_window_size).one()
    sentiment = session.query(DailySentScore).where(DailySentScore.topic_id == topic_id,
                                                    DailySentScore.date == day,
                                                    DailySentScore.window_size==max_corr_window_size).one()
    return CorrLineModel(date=day, sentiment=round(sentiment.sent_score, 3),
                         snp500=round(index.snp500, 3), nasdaq100=round(index.nasdaq100, 3))


def get_corr_model_and_max_window(topic: Topic):
    window_sizes = []
    snp500 = []
    nasdaq100 = []
    for correlation in topic.correlations:
        window_sizes.append(correlation.window_size)
        snp500.append(round(correlation.snp500_corr,3))
        nasdaq100.append(round(correlation.nasdaq100_corr,3))
    mean_corrs = [abs((snp500[i]+nasdaq100[i])/2) for i in range(len(snp500))]
    max_corr_window_size = mean_corrs.index(max(mean_corrs)) + 1
    return CorrelationModel(window_sizes=window_sizes, snp500=snp500, nasdaq100=nasdaq100), max_corr_window_size
