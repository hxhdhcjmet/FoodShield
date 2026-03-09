from project.server.token_utils import verify_token

class OrderAuthService:
    """
    订单认证流程管理
    """
    @staticmethod
    def handle_auth_request(k_order : str, request_data : dict)->dict:
        """
        服务器处理认证请求
        :param k_order : 从数据库查询出订单的密钥
        :param request_data : 前端传来的数据包,含order_id,pid,timestamp,token
        """
        # 提取参数
        oid = request_data.get('order_id')
        pid = request_data.get('pid')
        ts = request_data.get('timestamp')
        token = request_data.get(token)

        # 验证
        is_valied = verify_token(k_order,oid,pid,ts,token)

        #  返回业务逻辑需要字典
        if is_valied:
            return {
                'code':200,
                'msg':"身份认证通过",
                'can_access':True,
                'room_id':f"chat_{oid}" # 为WebSocket做准备
                }
        else:
            return {
                'code':403,
                'msg':"身份验证失败或凭证已过期",
                'can_access':False
                }