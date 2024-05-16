import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_SLOWLOG_COLLECTION_NAME = os.getenv("MONGODB_SLOWLOG_COLLECTION_NAME")
MONGODB_DIGEST_COLLECTION_NAME = os.getenv("MONGODB_DIGEST_COLLECTION_NAME")
MONGODB_STATUS_COLLECTION_NAME = os.getenv("MONGODB_STATUS_COLLECTION_NAME")
MONGODB_PLAN_COLLECTION_NAME = os.getenv("MONGODB_PLAN_COLLECTION_NAME")
MONGODB_HISTORY_COLLECTION_NAME = os.getenv("MONGODB_HISTORY_COLLECTION_NAME")
MONGODB_AURORA_INFO_COLLECTION_NAME = os.getenv("MONGODB_AURORA_INFO_COLLECTION_NAME")
MONGODB_RDS_INSTANCE_LIST_COLLATION_NAME = os.getenv("MONGODB_RDS_INSTANCE_LIST_COLLATION_NAME")

# MySQL에서 고려하는 슬로우 쿼리의 최소 실행 시간 (단위: 초)
EXEC_TIME = 1