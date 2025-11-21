"""
WebSocket 实时通信端点
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import json
from datetime import datetime

router = APIRouter()


# ==================== 连接管理器 ====================

class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 用户ID -> WebSocket连接列表（支持多设备）
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """建立连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"用户 {user_id} 已连接，当前连接数: {self.get_online_count()}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """断开连接"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"用户 {user_id} 已断开，当前连接数: {self.get_online_count()}")

    async def send_personal_message(self, message: dict, user_id: str):
        """发送私人消息"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"发送消息失败: {e}")

    async def broadcast(self, message: dict):
        """广播消息给所有用户"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"广播消息失败: {e}")

    def is_online(self, user_id: str) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections

    def get_online_count(self) -> int:
        """获取在线用户数"""
        return len(self.active_connections)

    def get_online_users(self) -> List[str]:
        """获取在线用户列表"""
        return list(self.active_connections.keys())


# 全局连接管理器
manager = ConnectionManager()


# ==================== WebSocket 端点 ====================

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)  # 通过 URL 参数传递 token
):
    """
    WebSocket 连接端点
    连接方式: ws://localhost:8000/api/v1/ws?token=<jwt_token>
    """
    # TODO: 验证 token 并获取用户ID
    # user_id = verify_token(token)
    user_id = "test_user"  # 模拟

    await manager.connect(websocket, user_id)

    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })

        # 持续监听消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            await handle_message(websocket, user_id, message)

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        manager.disconnect(websocket, user_id)


async def handle_message(websocket: WebSocket, user_id: str, message: dict):
    """
    处理收到的 WebSocket 消息
    """
    msg_type = message.get("type")

    if msg_type == "ping":
        # 心跳检测
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })

    elif msg_type == "chat":
        # 聊天消息
        recipient_id = message.get("to")
        content = message.get("content")

        if recipient_id and content:
            # 发送给接收者
            chat_message = {
                "type": "chat",
                "from": user_id,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(chat_message, recipient_id)

            # 确认发送成功
            await websocket.send_json({
                "type": "chat_sent",
                "to": recipient_id,
                "timestamp": datetime.now().isoformat()
            })

            # TODO: 保存消息到数据库

    elif msg_type == "typing":
        # 正在输入状态
        recipient_id = message.get("to")
        if recipient_id:
            await manager.send_personal_message({
                "type": "typing",
                "from": user_id
            }, recipient_id)

    elif msg_type == "read":
        # 消息已读回执
        message_id = message.get("message_id")
        sender_id = message.get("sender_id")
        if message_id and sender_id:
            await manager.send_personal_message({
                "type": "read_receipt",
                "message_id": message_id,
                "reader": user_id
            }, sender_id)


# ==================== HTTP API 端点 ====================

@router.get("/online-count")
async def get_online_count():
    """获取在线用户数"""
    return {"count": manager.get_online_count()}


@router.get("/online-users")
async def get_online_users():
    """获取在线用户列表"""
    return {"users": manager.get_online_users()}


@router.get("/is-online/{user_id}")
async def check_user_online(user_id: str):
    """检查用户是否在线"""
    return {"online": manager.is_online(user_id)}


# ==================== 辅助函数（供其他模块调用） ====================

async def push_notification(user_id: str, notification: dict):
    """
    推送通知给用户
    可在其他模块中调用
    """
    message = {
        "type": "notification",
        **notification,
        "timestamp": datetime.now().isoformat()
    }
    await manager.send_personal_message(message, user_id)


async def broadcast_announcement(title: str, content: str):
    """
    广播系统公告
    """
    await manager.broadcast({
        "type": "announcement",
        "title": title,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
