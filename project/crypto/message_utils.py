import hashlib

def calculate_message_hash(order_id, sender_pid, role, content, timestamp):
    raw = f"{order_id}|{sender_pid}|{role}|{content}|{timestamp}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()