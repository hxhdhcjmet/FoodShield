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
    # message_str = f"{order_id}{sender_pid}{content}{timestamp}"
    # '|'拼接分隔可以防止出现如 12+3 = 1+23= 123 的碰撞
    message_str = "|".join([order_id,sender_pid,content,timestamp])

    return generate_hash(message_str)

class MerkleTree:
    """
    基于迭代列表的轻量级、高性能Merkle Tree
    """
    def __init__(self,leaves : list):
        # leaves为包含多条消息 msg_hash 的列表
        self.leaves = leaves

    def get_root(self)->str:
        """
        计算并返回Merkle Root
        """
        # 如果没有日志,返回固定空字符串的Hash
        if not self.leaves:
            return generate_hash("")
        
        current_level = self.leaves

        # 当前层级的节点数大于1时,继续向上构建
        while len(current_level) > 1:
            next_level = []

            # 步长为2,两两提取节点
            for i in range(0,len(current_level),2):
                left = current_level[i]
                # 奇数个节点时,复制最后一个节点让它自己配对,防止落单
                if i+1 < len(current_level):
                    right = current_level[i+1]
                else:
                    right = left
                # 拼接左右哈希值并进行二次哈希
                combined = left + right
                next_level.append(generate_hash(combined))

            # 新的一层赋值给当前层,继续下一次while循环
            current_level = next_level
        return current_level[0]



if __name__ == "__main__":
    print("="*30,"测试Merkle Tree","="*30)

    h1 = generate_hash('msg1')
    h2 = generate_hash('msg2')
    h3 = generate_hash('msg3')
    leaves_list = [h1,h2,h3]
    tree = MerkleTree(leaves_list)

    root = tree.get_root()

    print(f"叶子节点数:{len(leaves_list)}")
    print(f"生成的mekle root:{root}")

    print("="*30,"测试篡改","="*30)
    h4fake = generate_hash('msg4')
    changed_leaves = [h1,h2,h3,h4fake]
    fake_tree = MerkleTree(changed_leaves)
    fake_root = fake_tree.get_root()
    print(f"叶子节点数:{len(changed_leaves)}")
    print(f"篡改后的merkle root:{fake_root}")
    






    