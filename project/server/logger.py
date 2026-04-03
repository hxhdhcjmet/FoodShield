# 消息记录模块
import time
from project.crypto.merkle import hash_message,MerkleTree
from project.database.db import query_all
class CommunicationLogger:
    """
    消息记录模块
    负责接收聊天信息,计算其Hash,并储存到内存中的日志结构里
    """
    def __init__(self):
        self.chat_logs = {} # 存储聊天记录
        self.audit_roots = {}# 存储已认证的Merkle Root

        # 初步使用字典储存,方便后续转数据库,直接一步到数据库需要与后端频繁对接,降低开发效率
        # key:order_id,value:该订单下的所有聊天记录列表
        #{
            # "order_001":[
            #  {"sender_pid":"PID_A","content":"您好,马上到","timestamp":...,"msg_hash":"..."},
            #  {"sender_pid":"PID_B","content":"好的,马上下去取","timestamp":...,"msg_hash":...}
        #   ]
        #}

    def record_chat_message(self,order_id : str, sender_pid : str, content : str)->dict:
        """
        供WebSocket调用的接口:记录一条聊天信息并返回其完整结构
        """
        timestamp = str(int(time.time()))
        msg_hash = hash_message(order_id,sender_pid,content,timestamp)

        # 构建单条日志结构
        log_entry = {
            "order_id" : order_id,
            "sender_pid" : sender_pid,
            "content" : content,
            "timestamp" : timestamp,
            "msg_hash" : msg_hash
        }

        if order_id not in self.chat_logs:
            self.chat_logs[order_id] = []

        self.chat_logs[order_id].append(log_entry)
        print(f"[日志模块]已经安全记录订单{order_id}的消息,防篡改哈希 : {msg_hash[:8]}...")
        return log_entry
    
    def get_logs_by_order(self,order_id : str)->list:
        """
        查询接口:获取某个订单的所有聊天记录
        """
        return self.chat_logs.get(order_id,[])
    
    def seal_and_save_root(self,order_id : str)->str:
        """
        生成并封装Merkle Root(存证)
        """
        logs = self.chat_logs.get(order_id,[])
        hashes = [log['msg_hash'] for log in logs]

        tree = MerkleTree(hashes)
        root = tree.get_root()
        self.audit_roots[order_id] = root
        return root
    
    def verify_integrity(self,order_id : str)->tuple:
        """
        验证日志完整性: 从数据库读取当前真实数据，重新计算Root并与存证对比
        """
        saved_root = self.audit_roots.get(order_id)
        if not saved_root:
            return False, "未找到存证记录"
        
        # 【修正这里】直接调用 query_all，不要加 db.
        # 注意：这里的 SQL 语句要确保和你数据库中的表名、字段名对得上
        current_logs = query_all("SELECT * FROM messages WHERE order_id = ?", (order_id,))

        if not current_logs:
            return False, "数据库中未找到相关聊天记录"

        # 重新计算哈希列表
        current_hashes = []
        for log in current_logs:
            # 根据你数据库的字段名提取数据，重新计算每一条消息的哈希
            # 这里的字段名（如 order_id, sender_pid 等）必须与数据库表结构完全一致
            h = hash_message(
                str(log['order_id']), 
                str(log['sender_pid']), 
                str(log['content']), 
                str(log['timestamp'])
            )
            current_hashes.append(h)

        # 构建当前的 Merkle Tree
        current_root = MerkleTree(current_hashes).get_root()

        if current_root == saved_root:
            return True, "验证通过: 日志完整"
        else:
            return False, "警告: 检测到日志篡改"
        
    
if __name__ == "__main__":
    logger = CommunicationLogger()

    order_id = "0001"
    user_id = "USER_0001"
    rider_id = "RIDER_PID_0001"

    print("="*50,"测试","="*50)
    print("骑手发送信息")
    rider_msg = logger.record_chat_message(order_id,rider_id,"你好,你的外卖到了")
    time.sleep(1)

    print("用户回复信息")
    user_msg = logger.record_chat_message(order_id,user_id,"收到,马上去取")

    root = logger.seal_and_save_root(order_id)
    print(f"原始merkle root:{root}")

    # 模拟完整性校验
    success,msg = logger.verify_integrity(order_id)
    print(f"初次审计结果:{success},信息:{msg}")

    # 模拟攻击
    print("模拟黑客攻击...")
    logger.chat_logs[order_id][0]['content'] = "我把外卖偷走了"
    l = logger.chat_logs[order_id][0]
    logger.chat_logs[order_id][0]['msg_hash'] = hash_message(order_id,l['sender_pid'],l['content'],l['timestamp'])

    # 再次进行merkle审计
    success,msg = logger.verify_integrity(order_id)
    print(f'篡改后审计结果:{success},信息:{msg}')





        


