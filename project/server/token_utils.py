import time
import hmac
import hashlib
from project.crypto.auth_utils import HMACAuth

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
    message = f"{order_id}{pid}{timestamp}"

    token = HMACAuth.sign(k_order,message)
    return {"token" : token,"timestamp" : timestamp}

def verify_token(k_order : str, order_id : str, pid : str, timestamp : str, provided_token : str,expired_seconds : int = 3600)->bool:
    """
    业务层函数,验证订单凭证
    """
    # 检测事件是否过期
    curr_time = int(float(time.time()))
    if curr_time - int(timestamp) > expired_seconds:
        return False
    
    message = f"{order_id}{pid}{timestamp}"

    return HMACAuth.verify(k_order,message,provided_token)




if __name__ == "__main__":
    k_order = "FoodShield"
    order_id = "001"
    pid = "asdfghjkl"
    result = generate_token(k_order,order_id,pid)

    token = result['token']
    timestamp = result['timestamp']

    # 验证通过
    print(verify_token(k_order,order_id,pid,timestamp,token))

    # 过期:
    time.sleep(1)
    print(verify_token(k_order,order_id,pid,timestamp,token,expired_seconds=0))

    # 错误id
    print(verify_token(k_order,'112233','22334455',timestamp,token))

