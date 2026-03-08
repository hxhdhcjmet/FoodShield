import hmac
import hashlib
import secrets


def generate_pid(k_master : str, user_id : str)->dict:
    """
    生成用户匿名身份标识(PID)
    公式: PID = HMAC(K_master , userID || r)
    : param k_master : 系统主密钥,由系统统一安全保管
    : param user_id : 用户真实ID
    : return 包含pid和所用随机数r的字典
    """

    # 生成16字节安全随机数作为 r
    r = secrets.token_hex(16)

    # 拼接user_id 和 r
    message = f"{user_id}{r}".encode('utf-8')
    key = k_master.encode('utf-8')

    # HMAC-SHA256算法生成PID
    pid = hmac.new(key,message,hashlib.sha256).hexdigest()

    return {"pid" : pid,'r' : r}

if __name__ == "__main__":
    k = "FoodShield"
    user_id = 'user001'
    print(generate_pid(k,user_id))