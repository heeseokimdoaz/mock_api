import os

# 2/23 이후 실제 API로 교체할 때 이 환경변수만 변경하면 됩니다.
# export TAPACROSS_API_URL=http://api.trendup.co.kr
API_BASE_URL = os.getenv("TAPACROSS_API_URL", "http://localhost:8000")
CLIENT_ID = os.getenv("TAPACROSS_CLIENT_ID", "mock_client_123")
SEARCH_ID = os.getenv("TAPACROSS_SEARCH_ID", "10")
