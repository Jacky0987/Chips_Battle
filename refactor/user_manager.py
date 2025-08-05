import json
import hashlib
import os
import base64
from cryptography.fernet import Fernet
from datetime import datetime


class UserManager:
    def __init__(self):
        self.users_file = "users_data.json"
        self.current_user = None
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def _get_or_create_key(self):
        key_file = "game.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _encrypt_data(self, data):
        json_data = json.dumps(data)
        encrypted_data = self.cipher.encrypt(json_data.encode())
        return base64.b64encode(encrypted_data).decode()

    def _decrypt_data(self, encrypted_data):
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return json.loads(decrypted_data.decode())
        except:
            return None

    def load_users(self):
        if not os.path.exists(self.users_file):
            return {}

        try:
            with open(self.users_file, 'r') as f:
                encrypted_data = f.read()
                if encrypted_data:
                    return self._decrypt_data(encrypted_data) or {}
                return {}
        except:
            return {}

    def save_users(self, users_data):
        encrypted_data = self._encrypt_data(users_data)
        with open(self.users_file, 'w') as f:
            f.write(encrypted_data)

    def register_user(self, username, password, email=""):
        users = self.load_users()
        if username in users:
            return False, "用户名已存在"

        users[username] = {
            'password': self._hash_password(password),
            'email': email,
            'created_date': datetime.now().isoformat(),
            'game_data': {
                'cash': 100000.0,
                'portfolio': {},
                'transaction_history': [],
                'achievements': [],
                'level': 1,
                'experience': 0,
                'total_profit': 0,
                'best_trade': 0,
                'trades_count': 0,
                'login_streak': 0,
                'last_login': None,
                'game_settings': {
                    'sound_enabled': True,
                    'notifications_enabled': True,
                    'auto_save': True
                }
            }
        }

        self.save_users(users)
        return True, "注册成功"

    def login_user(self, username, password):
        users = self.load_users()
        if username not in users:
            return False, "用户不存在"

        if users[username]['password'] != self._hash_password(password):
            return False, "密码错误"

        # 检查用户是否被封禁
        if users[username].get('banned', False):
            return False, "账户已被封禁，请联系管理员"

        self.current_user = username

        # 更新登录信息
        today = datetime.now().date()
        last_login = users[username]['game_data'].get('last_login')

        if last_login:
            last_login_date = datetime.fromisoformat(last_login).date()
            if (today - last_login_date).days == 1:
                users[username]['game_data']['login_streak'] += 1
            elif (today - last_login_date).days > 1:
                users[username]['game_data']['login_streak'] = 1
        else:
            users[username]['game_data']['login_streak'] = 1

        users[username]['game_data']['last_login'] = datetime.now().isoformat()
        self.save_users(users)

        return True, "登录成功"

    def get_user_data(self, username=None):
        if not username:
            username = self.current_user
        if not username:
            return None

        users = self.load_users()
        return users.get(username, {}).get('game_data', {})

    def save_user_data(self, game_data, username=None):
        if not username:
            username = self.current_user
        if not username:
            return

        users = self.load_users()
        if username in users:
            users[username]['game_data'] = game_data
            self.save_users(users)
