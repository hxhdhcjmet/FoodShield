import hashlib


def generate_hash(data : str)->str:
    """
    基础Hash生成函数,用于计算消息Hash、构建Merkle Tree
    :param data : 需要计算哈希值的原始字符串
    :return : 64位十六进制字符串
    """

    return hashlib.sha256(data.encode('utf-8')).hexdigest()


if __name__ == "__main__":
    data = "hello world"
    print(generate_hash(data))




    