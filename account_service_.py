from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import os
import redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:20040219@localhost:5432/sports'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 一级缓存
cache = {}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

def create_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    redis_client.set(f"user:{user_id}:token", token)
    redis_client.expire(f"user:{user_id}:token", timedelta(hours=1))
    # 存储到一级缓存
    cache[f"user:{user_id}:token"] = token
    return token

def verify_jwt_token(token):
    # 首先检查一级缓存
    for user_key, cached_token in cache.items():
        if cached_token == token:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload['user_id']
    
    # 如果一级缓存中没有，检查 Redis
    for user_key in redis_client.scan_iter("user:*:token"):
        stored_token = redis_client.get(user_key)
        if stored_token == token:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # 将令牌加载到一级缓存
            cache[user_key] = stored_token
            return payload['user_id']
    
    return None

@app.route('/user/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not all([username, password, email]):
        return jsonify(msg="参数不完整", code=4000), 400
    if len(password) < 8:
        return jsonify(msg="密码长度至少为8位", code=4001), 400
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify(msg="用户名或邮箱已存在", code=4002), 400
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify(msg="注册成功", code=200, username=username)

@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if user is None or not check_password_hash(user.password, password):
        return jsonify(msg="用户名或密码错误", code=4001), 401
    token = create_jwt_token(user.id)
    session['user_id'] = user.id
    return jsonify(msg="登录成功", code=200, token=token)

@app.route('/user/session', methods=['GET'])
def check_session():   
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify(msg="请先登陆再尝试", code=4000), 400
    token = token.split(' ')[1]
    user_id = verify_jwt_token(token)
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify(username=user.username, code=200)
        else:
            return jsonify(msg="用户不存在", code=404), 404
    else:
        return jsonify(msg="无效的令牌,重新登陆试试", code=4001), 401

@app.route('/user/logout', methods=['DELETE'])
def logout():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify(msg="无令牌提供", code=4000), 400
    
    token = token.split(' ')[1]
    user_id = verify_jwt_token(token)

    if user_id:
        # 构造 Redis 键
        redis_key = f"user:{user_id}:token"
        print(f"Attempting to delete token with key: {redis_key}")

        # 检查 Redis 中是否存在键
        stored_token = redis_client.get(redis_key)
        if stored_token:
            delete_status = redis_client.delete(redis_key)
            if delete_status == 1:
                # 从一级缓存中删除
                cache.pop(redis_key, None)
                return jsonify(msg="退出登录成功", code=200)
            else:
                return jsonify(msg="令牌删除失败", code=500), 500
        else:
            return jsonify(msg="令牌不存在", code=404), 404
    else:
        return jsonify(msg="无效的令牌", code=4001), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)