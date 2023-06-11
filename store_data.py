# 모델에서 나온 결과 저장

# 지금은 모델에서 나온 결과를 파일로 받지만 나중에는 파이프라인처럼 한방에
import pickle
import pandas as pd
from models import *
from datetime import datetime, date
from database import get_db
from process_data import get_topic_words, get_sent_dist, get_topic_proportions, get_sentiment_score, get_correlation
from store_stock_index import snp500, nasdaq100

session = get_db()
# sent_dists = []
# topic_words = []
# topic_proportions = []
# sent_scores = []
total_tweet_number = 0

# 나중에는 여기서 lda 불러올 필요 없음. 모델 돌릴때 이미 있음
with open('lda_6_9.pickle', 'rb') as fp:
    lda = pickle.load(fp)

# 앞으로 카운트벡터도 피클로 저장해야 함
with open('count_vect_6_9.pickle', 'rb') as fp:
    count_vect = pickle.load(fp)

for i in range(10):  # 토픽 개수(=SA 돌린 횟수)만큼 반복
    df = pd.read_csv(f'drive-download-20230610T134303Z-001/topic_{i}_text.csv', lineterminator='\n')  # 나중엔 이거 필요 ㄴㄴ
    tweet_number = len(df)
    total_tweet_number += tweet_number
    topic = Topic(topic_name=f'토픽이름{i}', tweet_number=tweet_number,
                  create_date=datetime.now())

    session.add(topic)

    df['sentiment'] = df[['negative', 'neutral', 'positive']].idxmax(axis=1)  # 감성 레이블링

    # total_df 쌓기
    if i==0:
        total_df = df
    else:
        total_df = pd.concat([total_df, df])

    # # 감성분포 배열 만들기
    # sent_dists.append(get_sent_dist(df, tweet_number))
    neg, neu, pos = get_sent_dist(df, tweet_number)
    sd = SentDist(pos_percent=int(pos * 100), neg_percent=int(neg * 100), neutral_percent=int(neu * 100),
                  create_date=datetime.now(), topic=topic)
    session.add(sd)

    # #워드클라우드
    # wordclouds.append(get_topic_words(lda, i))
    topic_words = get_topic_words(lda, i, count_vect.get_feature_names_out())
    for word, value in topic_words:
        tw = TopicWord(word=word, value=value, create_date=datetime.now(), topic=topic)
        session.add(tw)

    # 감성키워드 -> 나중에 pmi로 구하고 정렬해서 저장
    for t in range(1,7):
        sk = SentKeyword(keyword=f'keyword{t}', value=80 if t<4 else -80, topic=topic, create_date=datetime.now())
        session.add(sk)

    # 일별감성점수
    daily_sent_score = get_sentiment_score(df)
    days = list(daily_sent_score.index)
    for idx, day in enumerate(days):
        y, m, d = int(day[:4]), int(day[5:7]), int(day[8:])
        dss = DailySentScore(date=date(y,m,d), sent_score=daily_sent_score[idx], create_date=datetime.now(), topic=topic)
        session.add(dss)

    # 상관관계
    snp500_corr = get_correlation(daily_sent_score, snp500)
    nasdaq100_corr = get_correlation(daily_sent_score, nasdaq100)

    c = Correlation(refer_day=1, snp500_corr=snp500_corr, nasdaq100_corr=nasdaq100_corr, create_date=datetime.now(),
                    topic=topic)
    session.add(c)
    print(f'{i}번 토픽 저장!')

# topic10: 전체
topic = Topic(topic_name='전체토픽', tweet_number=total_tweet_number, create_date=datetime.now())
session.add(topic)
neg, neu, pos = get_sent_dist(df, tweet_number)
sd = SentDist(pos_percent=int(pos * 100), neg_percent=int(neg * 100), neutral_percent=int(neu * 100),
              create_date=datetime.now(), topic=topic)
session.add(sd)
print('전체 토픽 저장!')

session.commit()

    # 토픽분포
days, proportions = get_topic_proportions(total_df, lda, count_vect)
for i, daily_proportions in enumerate(proportions):
    print(f'{i+1}번 토픽 시작')
    topic = session.query(Topic).get(i+1)
    for j, proportion in enumerate(daily_proportions):
        tp = DailyTopicProportion(date=days[j], proportion=proportion, create_date=datetime.now(), topic=topic)
        session.add(tp)
    print(f'{i+1}번 토픽분포 저장!')


session.commit()
