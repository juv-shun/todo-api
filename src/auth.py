import os

from fastapi_cloudauth.cognito import CognitoCurrentUser

get_current_user = CognitoCurrentUser(
    region=os.getenv("REGION", "ap-northeast-1"),
    userPoolId=os.environ["USER_POOL_ID"],
    client_id=os.environ["APP_CLIENT_ID"],
)
