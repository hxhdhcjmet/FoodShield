# 消息记录模块
import time
from project.crypto.merkle import hash_message

class CommunicationLogger:
    """
    消息记录模块
    负责接收聊天信息,计算其Hash,并储存到内存中的日志结构里
    """
    def __init__(self):
        self.chat_logs = {}

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

    print('+'*30,"打印储存在系统的信息",'+'*30)
    all_logs = logger.get_logs_by_order(order_id)

    for idx,log in enumerate(all_logs):
        print(f"第{idx+1}条信息记录")
        print(f"发送方PID:{log['sender_pid']}")
        print(f"明文信息:{log['content']}")
        print(f"时间戳:{log['timestamp']}")
        print(f"完整Hash凭证:{log['msg_hash']}")



        


