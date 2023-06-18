# 모델에서 나온 결과 저장

# 지금은 모델에서 나온 결과를 파일로 받지만 나중에는 파이프라인처럼 한방에
import pickle
import pandas as pd
from models import *
from datetime import datetime, date
from database import Session
from process_data import get_topic_words, get_sent_dist, get_topic_proportions, get_sentiment_score, get_correlation
from time_series_data import snp500, nasdaq100, datelist

session = Session()
sent_dists = []
# topic_words = []
# topic_proportions = []
# sent_scores = []
total_tweet_number = 0

snp_windows = []
nasdaq_windows = []

# window 사이즈별 snp, nasdaq 등락률 구하고 저장
for j in range(1,6):
    window = j + 1
    snp = [(snp500[i - 1] - snp500[i - window]) / snp500[i - window] for i in range(window, len(snp500) + 1)]
    snp_windows.append(snp)
    nasdaq = [(nasdaq100[i - 1] - nasdaq100[i - window]) / nasdaq100[i - window] for i in range(window, len(nasdaq100) + 1)]
    nasdaq_windows.append(nasdaq)
    for idx, day in enumerate(datelist[j:]):
        di = DailyIndex(date=day, window_size=j, snp500=snp[idx], nasdaq100=nasdaq[idx], create_date=datetime.now())
        session.add(di)
print('daily index 저장!')
session.commit()
#
# # 나중에는 여기서 lda 불러올 필요 없음. 모델 돌릴때 이미 있음
# with open('lda_6_13.pickle', 'rb') as fp:
#     lda = pickle.load(fp)
#
# # 앞으로 카운트벡터도 피클로 저장해야 함
# with open('count_vect_6_13.pickle', 'rb') as fp:
#     count_vect = pickle.load(fp)
#
# # topic_names = [] <- 토픽 이름 정하면 앞으로 이대로 쓰기
#
# for i in range(10):  # 토픽 개수(=SA 돌린 횟수)만큼 반복
#     print(f'{i}번째 토픽 시작!')
#     df = pd.read_csv(f'drive-download-20230618T165948Z-001/result_topic_{i}_text.csv', lineterminator='\n')  # 나중에 걍 경로 지정
#     tweet_number = len(df)
#     total_tweet_number += tweet_number
#     topic = Topic(topic_name=f'토픽이름{i}', tweet_number=tweet_number,
#                   create_date=datetime.now())
#
#     session.add(topic)
#
#     # 상관관계, 일별 감성 점수
#     corr_results = []
#
#     for window in range(1,6):
#         print(f'window{window}')
#         sent_index_df, snp500_corr, nasdaq100_corr = get_correlation(df, snp_windows[window-1], nasdaq_windows[window-1], window)
#         c = Correlation(window_size=window, snp500_corr=snp500_corr, nasdaq100_corr=nasdaq100_corr, create_date=datetime.now(),
#                         topic=topic)
#         session.add(c)
#         for idx, day in enumerate(sent_index_df.agg_date):
#             dss = DailySentScore(date=day, window_size=window, sent_score=sent_index_df.agg_score[idx],
#                                  create_date=datetime.now(), topic=topic)
#             session.add(dss)
#     print('correlation, daily sent score 저장!')
#
#
#
#     df['sentiment'] = df[['negative', 'neutral', 'positive']].idxmax(axis=1)  # 감성 레이블링
#
#     # total_df 쌓기
#     if i==0:
#         total_df = df
#     else:
#         total_df = pd.concat([total_df, df])
#
#     # 감성분포
#     sent_dists.append(get_sent_dist(df, tweet_number))
#     neg, neu, pos = get_sent_dist(df, tweet_number)
#     sd = SentDist(pos_percent=int(pos * 100), neg_percent=int(neg * 100), neutral_percent=int(neu * 100),
#                   create_date=datetime.now(), topic=topic)
#     session.add(sd)
#     print('sent_dist 저장!')
#
#     # #워드클라우드
#     # wordclouds.append(get_topic_words(lda, i))
#     topic_words = get_topic_words(lda, i, count_vect.get_feature_names_out())
#     for word, value in topic_words:
#         tw = TopicWord(word=word, value=value, create_date=datetime.now(), topic=topic)
#         session.add(tw)
#     print('워드클라우드 저장!')
#
#     # 감성키워드 -> 나중에 pmi로 구하고 '정렬해서' 저장
#     for t in range(1,7):
#         sk = SentKeyword(keyword=f'keyword{t}', value=80 if t<4 else -80, topic=topic, create_date=datetime.now())
#         session.add(sk)
#     print('감성 키워드 저장!')
#
#
#     print(f'{i}번 토픽 저장!')
#
# # topic10: 전체
# topic = Topic(topic_name='전체토픽', tweet_number=total_tweet_number, create_date=datetime.now())
# session.add(topic)
# neg, neu, pos = get_sent_dist(total_df, total_tweet_number)
# sd = SentDist(pos_percent=int(pos * 100), neg_percent=int(neg * 100), neutral_percent=int(neu * 100),
#               create_date=datetime.now(), topic=topic)
# session.add(sd)
# print('전체 토픽 저장!')
#
# session.commit()
#
#     # 토픽분포
# days, proportions = get_topic_proportions(total_df, lda, count_vect)
# for i, daily_proportions in enumerate(proportions):
#     print(f'{i+1}번 토픽 시작')
#     topic = session.get(Topic, i+1)
#     for j, proportion in enumerate(daily_proportions):
#         tp = DailyTopicProportion(date=days[j], proportion=proportion, create_date=datetime.now(), topic=topic)
#         session.add(tp)
#     print(f'{i+1}번 토픽분포 저장!')
#
#
# session.commit()
