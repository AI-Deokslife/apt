from app import app

if __name__ == "__main__":
    # 모든 네트워크 인터페이스에서 접속 허용 (IP 접속 가능)
    app.run(host='0.0.0.0', port=5000, debug=False) 