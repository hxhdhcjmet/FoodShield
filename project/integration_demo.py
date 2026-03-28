# 系统整合与演示
# - 测试Merkle Tree日志完整性
# - 测试安全机制

import time 
from crypto.pid import generate_pid
from server.logger import CommunicationLogger
from server.security_audit import SecurityAuditor
from crypto.token_utils import generate_token,verify_token

def run_system_integration_test():
    """
    全链路系统集成测试与演示
    """
    print("="*60)
    print("外卖平台匿名订单认证系统 - 全链路安全演示")
    print("="*60)

    # 初始化核心系统
    k_master = "SYSTEM_MASTER_KEY_2026_3_28"
    k_order = "ORDER01"
    logger = CommunicationLogger()
    auditor = SecurityAuditor(logger)

    time.sleep(1)

    print("\n[阶段1] 匿名身份与订单认证")

    # 骑手与用户注册(生成PID)
    rider_info = generate_pid(k_master,"RIDER_REAL_ID")
    user_info = generate_pid(k_master,"USER_REAL_ID")
    rider_pid = rider_info["pid"]
    user_pid = user_info["pid"]
    print(f" √ 用户注册成功,生成匿名PID : {user_pid[:8]}...")

    # 用户下单
    order_id = "ORDER_2026_001"
    token_data = generate_token(order_id,user_pid)
    print(f" √ 订单生成成功,派发安全 Token : {token_data['token'][:8]}...")

    # 验证进入通信通道

    is_valid = verify_token(order_id,user_pid,token_data['timestamp'],token_data['token'])
    print(f" √ 订单认证校验结果 : {'通过(允许通信)'if is_valid else '拒绝'}" )
    time.sleep(1)

    # 第二阶段
    print("\n[阶段2] 匿名通信与日志防存证")

    # 模拟正常聊天
    logger.record_chat_message(order_id, rider_pid, "您的外卖送到了，请出来取一下。")
    logger.record_chat_message(order_id, user_pid, "好的，我这就出来，谢谢。")
    logger.record_chat_message(order_id, rider_pid, "不客气，祝您用餐愉快！")

    # 订单完成,生成Merkle Root 并存入系统审计库
    baseline_root = logger.seal_and_save_root(order_id)
    print(" √ 订单 {order_id} 交易结束。")
    print("f 日志已封存,生成 Merkle Root : {baseline_root}")

    time.sleep(1)

    # 第三阶段
    print("\n[阶段3] 安全审计与防篡改拦截测试")

    # 测试场景A:正常的完整性校验
    is_safe,msg = logger.verify_integrity(order_id)
    print(f" 第一次审计结果 : {'√ 安全 ' if is_safe else '× 危险'}({msg})")

    # 测试场景B:模拟黑客/内鬼篡改数据
    print("\n [警告] 检测到非法数据库操作...")
    print("-> 第一条消息修改为:'我把你的外卖吃了一半'")
    logger.chat_logs[order_id][0]['content'] = '我把你的外卖吃了一半'

    # 篡改甚至重新计算单条记录的Hash
    from crypto.merkle import hash_message
    tampered_log = logger.chat_logs[order_id][0]
    tampered_log['msg_hash'] = hash_message(order_id,tampered_log['sender_pid'],tampered_log['content'],tampered_log['timestamp'])

    # 测试场景C:系统溯源机制触发拦截

    print("\n[溯源触发] 管理员接到用户投诉外卖被吃,尝试提取证据链...")
    auditor_result = auditor.detect_security_violation(order_id,"外卖吃了一半")

    if not auditor_result['safe_to_trace']:
        print('安全模块成功拦截非法溯源!')
        print(f"拦截原因 : {auditor_result.get('message')}")
    else:
        print('严重错误,防线被突破!')

    print("\n" + "=" * 60)
    print("全链路集成测试完毕!各项安全机制运行正常!")
    print('='*60)

if __name__ == "__main__":
    run_system_integration_test()


                             

