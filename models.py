from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    keyword = db.Column(db.String(200), nullable=False)
    trade_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.Column(db.Text)  # JSON 형식으로 검색 결과 저장

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))  # Changed from password_hash
    is_admin = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_expiry = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    account_status = db.Column(db.String(20), default='활성')  # 활성, 휴면, 정지
    searches = db.relationship('Search', backref='user', lazy=True)
    
    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)  # Hash the password directly
        self.is_admin = is_admin
        self.is_premium = is_admin
        self.created_at = datetime.utcnow()
        
        # 무료 체험 기간 설정 (가입 기준 24시간)
        if not is_admin:
            self.subscription_expiry = self.created_at + timedelta(hours=24)
        else:
            self.subscription_expiry = self.created_at + timedelta(days=36500)  # 관리자는 100년
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_active(self):
        return self.account_status == '활성'
        
    def get_id(self):
        return str(self.id)
        
    def is_authenticated(self):
        return True
        
    def is_anonymous(self):
        return False 