from .logger import CommunicationLogger

class SecurityAuditor:
    """
    溯源模块
    """
    def __init__(self,logger_instance):
        # 传入CommunicationLogger实例
        self.logger = logger_instance

    def verify_og_authenticity(self,order_id : str)->bool:
        """
        日志验证功能,在进行溯源操作前,强制验证底层日志的Merkle Root 的完整性
        """
        print("正在校验订单{order_id}的防篡改指纹(Merkle Root)...")
        is_valid,msg = self.logger.verify_integrity(order_id)

        if not is_valid:
            print(f"验证失败:{msg}")
            return False
        
        print(f"验证通过:日志未被篡改,证据链合法有效")
        return True
    
    def detect_security_violation(self,order_id : str,suspicious_content : str)->dict:
        """
        基于合法日志,检验恶意言论并锁定作恶者的PID
        """
        print(f"正在日志中检索违规特征:{suspicious_content}...")
        if not self.verify_og_authenticity(order_id):
            # 已经被篡改了
            return {
            "safe_to_trace":False, # 被修改过记录不应该用来溯源
            "message":"证据链被污染,系统阻断溯源操作"    
            }
        
        logs = self.logger.chat_logs.get(order_id,[])
        malicious_pids = set()
        
        for log in logs:
            if suspicious_content in log["content"]:
                malicious_pids.add(log["sender_pid"])
        
        # 处理遍历结果
        if not malicious_pids:
            return {
            "safe_to_trace":False,
            "message":f"未命中:聊天记录中不存在 {suspicious_content},涉嫌恶意诬告,驳回溯源请求"                 
        }

        return {
        "safe_to_trace":True,
        "target_pids":list(malicious_pids),
        "message":"检测命中!已精确锁定涉嫌PID,准许溯源。"    
        }
    
if __name__ == "__main__":
    print("="*30,"条件溯源于安全测试","="*30)

    logger = CommunicationLogger()
    auditor = SecurityAuditor(logger)
    order_id = "001"

    # 模拟正常聊天
    logger.record_chat_message(order_id,"PID_1","外卖怎么还没到?")
    logger.record_chat_message(order_id,"PID_2","催什么催穷鬼")
    logger.seal_and_save_root(order_id)

    # 用户被骂后举报
    print("用户被骂后举报\n")
    result1 = auditor.detect_security_violation(order_id,"穷鬼")
    print(f"最终结果:允许溯源 = {result1['safe_to_trace']},说明 = {result1['message']}")

    # 恶意诬告
    print("用户恶意投诉骑手威胁\n")
    result2 = auditor.detect_security_violation(order_id,"我要打你")
    print(f"最终结果:允许溯源 = {result2['safe_to_trace']},说明 = {result2['message']}")

    # 内鬼篡改
    print("内部人员修改骂人的话为'马上就到'")
    logger.chat_logs[order_id][1]['content'] = '马上就到!'

    # 内鬼修改了该条hash试图掩盖
    from project.crypto.merkle import hash_message
    l = logger.chat_logs[order_id][1]
    logger.chat_logs[order_id][1]['msg_hash'] = hash_message(order_id,l['sender_pid'],l['content'],l['timestamp'])

    result3 = auditor.detect_security_violation(order_id,'穷鬼')
    print(f"最终结果:允许溯源:{result3['safe_to_trace']},说明 = {result3['message']}")


