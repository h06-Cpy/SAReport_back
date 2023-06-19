# SAReport_back
inisw 8조 백엔드 서버 구현
### 기술 스택
- FastAPI
  - DTO는 pydantic model 사용
- SQLAlchemy
- Alembic
- SQLite
### 프로세스
1. Sentiment Analysis 모델에서 나온 출력(csv) 파일을 이용하여 디비 스키마에 맞게 데이터 가공
2. 가공된 데이터를 SQLAlchemy를 통해 저장 -> 디비 구축
3. 구축된 디비에서 데이터를 꺼내고 pydantic을 이용해 DTO 생성
4. FastAPI를 통해 DTO를 프론트엔드에게 전달
