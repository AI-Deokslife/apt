# 부동산 검색 서비스

네이버 부동산 데이터 검색 및 엑셀 다운로드 서비스입니다.

## 로컬 개발 환경 설정

1. Python 3.8 이상 설치
2. 의존성 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```
3. 환경 변수 설정
   ```bash
   cp .env.example .env
   # .env 파일을 열어 실제 값으로 수정
   ```
4. 데이터베이스 초기화 및 서버 실행
   ```bash
   python app.py
   ```

## 웹 호스팅 서비스 배포 방법

### 공통 단계
1. 코드를 웹 호스팅 서비스에 업로드
2. 필요한 환경 변수 설정
   - `FLASK_ENV=production`
   - `SECRET_KEY=실제_안전한_키_값`
   - `DATABASE_URL=데이터베이스_연결_문자열`

### Heroku 배포
1. Heroku CLI 설치 및 로그인
2. 프로젝트 루트 디렉토리에서 다음 명령어 실행:
   ```bash
   heroku create 앱_이름
   git push heroku main
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=실제_안전한_키_값
   ```

### PythonAnywhere 배포
1. PythonAnywhere 계정 생성
2. 코드 업로드 (Git 또는 직접 업로드)
3. Web 탭에서 새 웹 앱 생성, "Flask" 선택
4. WSGI 구성 파일에서 경로를 `wsgi.py`로 설정
5. 가상 환경에서 `pip install -r requirements.txt` 실행
6. 환경 변수 설정

## 주의사항
- 실제 배포 환경에서는 `app.config['SECRET_KEY']`를 강력한 무작위 값으로 변경하세요.
- SQLite는 개발 환경에서만 사용하고, 프로덕션에서는 PostgreSQL 등 강력한 데이터베이스를 사용하세요.
- 프로덕션 환경에서는 HTTPS를 사용하여 통신을 암호화하세요. 