import time
from project.crypto.auth_utils import HMACAuth

K_ORDER = "FoodShield"

def generate_token(order_id: str, pid: str) -> dict:
    """
    生成订单认证凭证
    token = HMAC(K_order, order_id | pid | timestamp)
    """
    timestamp = str(int(time.time()))
    message = f"{order_id}|{pid}|{timestamp}"

    token = HMACAuth.sign(K_ORDER, message)
    return {
        "token": token,
        "timestamp": timestamp
    }

def verify_token(order_id: str, pid: str, timestamp: str, provided_token: str, expired_seconds: int = 3600) -> bool:
    """
    验证订单凭证
    """
    curr_time = int(time.time())

    # 检查是否过期
    if curr_time - int(timestamp) > expired_seconds:
        return False

    message = f"{order_id}|{pid}|{timestamp}"
    return HMACAuth.verify(K_ORDER, message, provided_token)


if __name__ == "__main__":
    order_id = "001"
    pid = "asdfghjkl"

    result = generate_token(order_id, pid)
    token = result["token"]
    timestamp = result["timestamp"]

    print(verify_token(order_id, pid, timestamp, token))
    time.sleep(1)
    print(verify_token(order_id, pid, timestamp, token, expired_seconds=0))
    print(verify_token("112233", "22334455", timestamp, token))
