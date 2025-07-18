# api/index.py

from flask import Flask, send_from_directory
from api.routes.backtest_route import bp as backtest_bp
from api.routes.scan_route import bp as scan_bp

# 1. 建立 Flask app 實例
app = Flask(__name__)

# 2. 註冊您的 API Blueprints
app.register_blueprint(backtest_bp)
app.register_blueprint(scan_bp)

# 3. (可選但推薦) 新增一個根路由來處理本地開發時的訪問
@app.route('/')
def serve_index():
    return send_from_directory('../public', 'backtest.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('../public', path)
