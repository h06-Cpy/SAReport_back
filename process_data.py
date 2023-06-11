import pandas as pd
from scipy import stats

def get_sent_dist(df, tweet_number):
    return (len(df[df['sentiment']=='negative'])/tweet_number, # 부정
            len(df[df['sentiment']=='neutral'])/tweet_number, # 중립
            len(df[df['sentiment']=='positive'])/tweet_number) # 긍정

def get_topic_words(lda, topic_num, feature_name):
    words = []

    topic = lda.components_[topic_num]
    # components_ array에서 가장 값이 큰 순으로 정렬했을 때, 그 값의 array index를 반환.
    topic_word_indexes = topic.argsort()[::-1]
    top_indexes = topic_word_indexes[:50]  # 상위 50개 단어만 추출

    for i in range(50):
        words.append((feature_name[topic_word_indexes[i]], round(topic[top_indexes[i]])))

    return words

def get_topic_proportions(total_df, lda, count_vect):
    # 토픽분포 --> 지금은 가지고 있는걸로만 구하지만 나중에는 lda 모델 돌린 후에 바로 구할 수 있음
    total_df.tweetDate = pd.to_datetime(total_df.tweetDate)
    daily_dfs = [day for day in total_df.groupby(total_df.tweetDate.dt.date)]
    days = [d[0] for d in daily_dfs]
    tmp = daily_dfs[0][1].copy()
    accum_dfs = [tmp]
    for day in daily_dfs[1:]:
        tmp = pd.concat([tmp, day[1]])
        accum_dfs.append(tmp)

    proportions = []
    for i in range(10): # 토픽 개수만큼
        proportions.append([])

    for idx, day in enumerate(accum_dfs):
        fit_vect = count_vect.fit_transform(total_df.text)
        doc_topic = pd.DataFrame(lda.transform(fit_vect))

        for i in range(10): # 토픽 개수만큼
            proportions[i].append(sum(doc_topic[i]) / len(day))

    return days, proportions

def get_sentiment_score(sentiment_df):
    sentiment_df['tweetDate'] = sentiment_df['tweetDate'].apply(lambda x: x.split()[0])

    # 긍정 부정 중립 중 가장 높은 점수를 해당 감성으로 치고 그 점수를 가져오는 함수
    # 이건 지금 중립 스코어까지 넣어버림.
    def highest(series):
        import numpy as np
        idx = np.argsort(series)[-1]
        result = series[idx]
        neg_idx = 0
        neu_idx = 1
        # 부정인 경우 -값으로 바꾼다.
        if idx == neg_idx:
            result = -result
        # 중성인 경우 강성 점수를 0으로 바꾼다.
        if idx == neu_idx:
            result = 0
        return result

    sentiment_df['agg_score'] = sentiment_df.iloc[:, -4:-1].apply(highest, axis=1)
    sentiment_score = sentiment_df.groupby('tweetDate').agg(sum)['agg_score'] / sentiment_df.groupby('tweetDate').size()
    return sentiment_score


def get_correlation(sentiment_score, stock_index, x_days=1):

    stock_index = stock_index[:len(sentiment_score)]

    return stats.pearsonr(sentiment_score, stock_index).statistic