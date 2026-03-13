import hmac
import hashlib
import secrets
import uuid


def generate_pid(k_master: str, user_id: str) -> dict:
    """
    生成用户匿名身份标识(PID)
    公式: PID = HMAC(K_master, userID || r)
    """
    r = secrets.token_hex(16)

    message = f"{user_id}{r}".encode("utf-8")
    key = k_master.encode("utf-8")

    pid = hmac.new(key, message, hashlib.sha256).hexdigest()

    return {"pid": pid, "r": r}
if __name__ == "__main__":
    k = "FoodShield"
    user_id = 'user001'
    print(generate_pid(k,user_id))