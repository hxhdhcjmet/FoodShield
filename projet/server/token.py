import time
import hmac
import hashlib


def generate_token(k_order : str, order_id : str, pid : str)->dict:
    """
    生成订单认证凭证
    公式 : token = HMAC(K_order,orderID || PID || timestamp)
    :param k-order : 订单密钥
    :param order_id : 订单唯一标识
    :param pid : 用户匿名身份标识
    :return token、timestamp的字典
    """

    # 获取时间戳
    timestamp = str(int(time.time()))

    # 拼接order_id,PID,timestamp
    message = f"{order_id}{pid}{timestamp}".encode('utf-8')
    key = k_order.encode('utf-8')

    # HMAC-SHA256算法生成Token
    token = hmac.new(key,message,hashlib.sha256).hexdigest()

    return {"token" : token,"timestamp" : timestamp}

if __name__ == "__main__":
    k_order = "FoodShield"
    order_id = "001"
    pid = "asdfghjkl"
    print(generate_token(k_order,order_id,pid))
