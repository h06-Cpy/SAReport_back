import pandas as pd
import numpy as np
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
        print(f'day {idx}')
        fit_vect = count_vect.fit_transform(day.text)
        doc_topic = pd.DataFrame(lda.transform(fit_vect))

        for i in range(10): # 토픽 개수만큼
            print(f'topic {i}: {sum(doc_topic[i]) / len(day)}')
            proportions[i].append(sum(doc_topic[i]) / len(day))

    return days, proportions

def get_sentiment_score(sentiment_df):
    sentiment_df['tweetDate'] = pd.to_datetime(sentiment_df['tweetDate'])
    date_group = sentiment_df.groupby(sentiment_df.tweetDate.dt.date)
    new_df = pd.DataFrame(columns=['date', 'agg_score'])

    for group in date_group:
        total_pos = 0
        total_neg = 0
        total_neu = 0

        pos_idx = 2
        neg_idx = 0
        neu_idx = 1

        date = group[0]
        df = group[1]
        total_tweet = df.shape[0]

        for i in df.iloc[:, -3:].values:
            idx = np.argsort(i)[-1]
            if idx == pos_idx:
                total_pos += 1
            if idx == neg_idx:
                total_neg += 1
            if idx == neu_idx:
                total_neu += 1

        result = ((total_pos - total_neg) / total_tweet) * (1 - (total_neu / total_tweet))
        new_df.loc[len(new_df) + 1] = [date, result]  # df에 추가
    return pd.Series(data=new_df['agg_score']).rename(new_df['date'])


def get_correlation(df, snp, nasdaq, window):
    sentiment_score = get_sentiment_score(df)
    window = window + 1

    agg_date = [sentiment_score.index[i - 1] for i in range(window, len(sentiment_score) + 1)]
    agg_score = [sentiment_score[i - window: i].mean() for i in range(window, len(sentiment_score) + 1)]

    print(f'agg_score len: {len(agg_score)}')
    print(f'snp len: {len(snp)}')
    print(f'nasdaq len: {len(nasdaq)}')

    # 일단 지금 결과는 하나의 값으로 나오는데 그래프 그리려면 위의 sentiment_score 배열 자체도 반환해야 함.
    return (pd.DataFrame(zip(agg_date, agg_score),
                        columns=['agg_date', 'agg_score']),
            stats.pearsonr(agg_score, snp).statistic,
            stats.pearsonr(agg_score, nasdaq).statistic)

