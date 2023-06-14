from database import Base
from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship


class Topic(Base):
    __tablename__ = 'topic'

    id = Column(Integer, primary_key=True)
    topic_name = Column(Text, nullable=False)
    tweet_number = Column(Integer, nullable=False)

    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=True)

    # sent_dist
    # topic_words
    # sent_keywords
    # daily_proportions
    # daily_sentscores
    # correlations

class SentDist(Base):
    __tablename__ = 'sent_dist'

    id = Column(Integer, primary_key=True)
    pos_percent = Column(Integer, nullable=False)
    neg_percent = Column(Integer, nullable=False)
    neutral_percent = Column(Integer, nullable=False)

    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=True)

    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship('Topic', backref='sent_dist')


class TopicWord(Base):
    __tablename__ = 'topic_word'

    id = Column(Integer, primary_key=True)
    word = Column(Text, nullable=False)
    value = Column(Integer, nullable=False)
    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=True)

    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship('Topic', backref='topic_words')


class SentKeyword(Base):
    __tablename__ = 'sent_keyword'

    id = Column(Integer, primary_key=True)
    keyword = Column(Text, nullable=False)
    value = Column(Float, nullable=False)
    create_date = Column(DateTime, nullable=True)
    last_update = Column(DateTime, nullable=True)

    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship('Topic', backref='sent_keywords')


class DailyTopicProportion(Base):
    __tablename__ = 'daily_topic_proportion'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    proportion = Column(Float, nullable=False)
    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=True)

    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship('Topic', backref='daily_proportions')


class DailySentScore(Base):
    __tablename__ = 'daily_sent_score'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    window_size = Column(Integer, nullable=False)
    sent_score = Column(Float, nullable=False)
    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=True)

    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship('Topic', backref='daily_sentscores')


class DailyIndex(Base):
    __tablename__ = 'daily_index'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    window_size = Column(Integer, nullable=False)
    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=True)

    # these values need to be normalized
    snp500 = Column(Float, nullable=False)
    nasdaq100 = Column(Float, nullable=False)

class Correlation(Base):
    __tablename__ = 'correlation'

    id = Column(Integer, primary_key=True)
    window_size = Column(Integer, nullable=False)

    snp500_corr = Column(Float, nullable=False)
    nasdaq100_corr = Column(Float, nullable=False)

    create_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=True)

    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship('Topic', backref='correlations')