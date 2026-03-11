import hashlib


def generate_hash(data : str)->str:
    """
    基础Hash生成函数,用于计算消息Hash、构建Merkle Tree
    :param data : 需要计算哈希值的原始字符串
    :return : 64位十六进制字符串
    """

    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def hash_message(order_id : str, sender_pid : str, content : str, timestamp : str)->str:
    """
    实现消息Hash计算.将核心通信字段拼接后计算哈希值,确保消息本身防篡改
    :param order_id : 订单号
    :param sender_pid : 发送方的匿名身份标识
    :param content : 聊天明文内容
    :param timestamp : 消息产生的时间戳
    :return : 消息体的哈希值(64位十六进制字符串)
    """
    message_str = f"{order_id}{sender_pid}{content}{timestamp}"

    return generate_hash(message_str)



if __name__ == "__main__":
    data = "hello world"
    print(generate_hash(data))




    