from datetime import datetime
from database import get_db
from time_series_data import snp500, nasdaq100, datelist
from models import DailyIndex


def normalization(x: float, max: float, min: float):
    """normalize number between -1 ~ 1"""
    return 2 * ((x - min) / (max - min)) - 1


session = get_db()


# 5.23~6.8


norm_snp = [normalization(x, max(snp500), min(snp500)) for x in snp500]
norm_nasdaq = [normalization(x, max(nasdaq100), min(nasdaq100)) for x in nasdaq100]

for i, day in enumerate(datelist):
    di = DailyIndex(date=day, snp500=norm_snp[i], nasdaq100=norm_nasdaq[i], create_date=datetime.now())
    session.add(di)
session.commit()
