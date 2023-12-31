import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_SLOWLOG_COLLECTION_NAME = os.getenv("MONGODB_SLOWLOG_COLLECTION_NAME")
MONGODB_STATUS_COLLECTION_NAME = os.getenv("MONGODB_STATUS_COLLECTION_NAME")
MONGODB_PLAN_COLLECTION_NAME = os.getenv("MONGODB_PLAN_COLLECTION_NAME")

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

# MySQL에서 고려하는 슬로우 쿼리의 최소 실행 시간 (단위: 초)
EXEC_TIME = 1

METRICS = [
    "AuroraBinlogReplicaLag",
    "ConnectionAttempts",
    "CPUUtilization",
    "DatabaseConnections",
    "Deadlocks",
    "DeleteThroughput",
    "DiskQueueDepth",
    "EngineUptime",
    "FreeableMemory",
    "InsertThroughput",
    "NetworkReceiveThroughput",
    "NetworkTransmitThroughput",
    "ReadIOPS",
    "ReadLatency",
    "ReadThroughput",
    "SelectThroughput",
    "SwapUsage",
    "UpdateThroughput",
    "WriteIOPS",
    "WriteLatency",
    "WriteThroughput",
    "Queries",
]
