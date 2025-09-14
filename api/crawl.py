from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
import urllib3
import openpyxl # Although not used for direct Excel saving in API, it's a dependency for the original script's logic.

# Suppress InsecureRequestWarning when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# 프록시 설정 (Vercel 환경에서는 필요 없을 수 있으나, 원본 코드에 있었으므로 유지)
proxies = {
    'http': None,
    'https': None,
}

# 거래 유형 매핑
TRADE_TYPE_MAPPING = {
    "전체": "",
    "매매": "A1",
    "전세": "B1",
    "월세": "B2"
}

# ------------------------ 데이터 수집 관련 함수 (GUI 독립 버전) ------------------------ #
def get_complexes_by_region_api(keyword):
    try:
        cookies = {
            'NNB': 'FGYNFS4Y6M6WO',
            'NFS': '2',
            'ASID': 'afd10077000001934e8033f50000004e',
            'ba.uuid': 'a5e52e8f-1775-4eea-9b42-30223205f9df',
            'tooltipDisplayed': 'true',
            'nstore_session': 'zmRE1M3UHwL1GmMzBg0gfcKH',
            '_fwb': '242x1Ggncj6Dnv0G6JF6g8h.1738045585397',
            'landHomeFlashUseYn': 'N',
            'REALESTATE': 'Thu Apr 03 2025 20:14:11 GMT+0900 (Korean Standard Time)',
            'NACT': '1',
        }
        headers = {
            'accept': '*/*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3MzgwNDcxNjMsImV4cCI6MTczODA1Nzk2M30.Heq-J33LY9pJDnYOqmRhTTrSPqCpChtWxka_XUphnd4',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        params = {'keyword': keyword, 'page': '1'}
        url = 'https://new.land.naver.com/api/search'
        
        session = requests.Session()
        session.headers.update(headers)
        session.cookies.update(cookies)
        session.proxies.update(proxies)

        # 세션 초기화
        init_url = 'https://new.land.naver.com/complexes'
        init_response = session.get(init_url, verify=False, timeout=10)
        init_response.raise_for_status()
        print(f"세션 초기화 성공: 상태 코드 {init_response.status_code}")

        print(f"지역 검색 API 요청 시작: {url}")
        response = session.get(url, params=params, timeout=30, verify=False)
        response.raise_for_status()
        print(f"지역 검색 API 응답 성공: 상태 코드 {response.status_code}")
        complexes = response.json().get('complexes', [])
        complexes.sort(key=lambda x: x['complexName'])
        return complexes
    except requests.exceptions.RequestException as e:
        print(f"Request error in get_complexes_by_region_api: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred in get_complexes_by_region_api: {e}")
        raise

def get_real_estate_data_api(complex_no, trade_type, page=1):
    try:
        cookies = {
            'NNB': 'FGYNFS4Y6M6WO',
            'NFS': '2',
            'ASID': 'afd10077000001934e8033f50000004e',
            'ba.uuid': 'a5e52e8f-1775-4eea-9b42-30223205f9df',
            'tooltipDisplayed': 'true',
            'nstore_session': 'zmRE1M3UHwL1GmMzBg0gfcKH',
            'nstore_pagesession': 'iH4K+dqWcpYFllsM1U4-116496',
            'NAC': 'XfPpC4A0XeLCA',
            'page_uid': 'iHmGBsqVN8ossOXBRrlsssssswV-504443',
            'nhn.realestate.article.rlet_type_cd': 'A01',
            'nhn.realestate.article.trade_type_cd': '""',
            'nhn.realestate.article.ipaddress_city': '1100000000',
            '_fwb': '242x1Ggncj6Dnv0G6JF6g8h.1738045585397',
            'realestate.beta.lastclick.cortar': '1174010900',
            'landHomeFlashUseYn': 'N',
            'BUC': 'fwUJCqRUIsM47V0-Lcz1VazTR9EQgUrBIxM1P_x9Id4=',
            'REALESTATE': 'Tue Jan 28 2025 16:23:02 GMT+0900 (Korean Standard Time)',
            'NACT': '1',
        }
        headers = {
            'accept': '*/*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3MzgwNDcxNjMsImV4cCI6MTczODA1Nzk2M30.Heq-J33LY9pJDnYOqmRhTTrSPqCpChtWxka_XUphnd4',
            'referer': f'https://new.land.naver.com/complexes/{complex_no}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        url = f'https://new.land.naver.com/api/articles/complex/{complex_no}'
        params = {
            'realEstateType': 'APT:PRE:ABYG:JGC',
            'tradeType': trade_type,
            'tag': '::::::::',
            'rentPriceMin': '0',
            'rentPriceMax': '900000000',
            'priceMin': '0',
            'priceMax': '900000000',
            'areaMin': '0',
            'areaMax': '900000000',
            'showArticle': 'false',
            'sameAddressGroup': 'false',
            'priceType': 'RETAIL',
            'page': str(page),
            'complexNo': str(complex_no),
            'type': 'list',
            'order': 'rank'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        session.cookies.update(cookies)
        session.proxies.update(proxies)

        # 세션 초기화
        init_url = f'https://new.land.naver.com/complexes/{complex_no}'
        init_response = session.get(init_url, verify=False, timeout=10)
        init_response.raise_for_status()
        print(f"매물 수집 세션 초기화 성공: 상태 코드 {init_response.status_code}")

        print(f"[DEBUG] API 요청 시작: {url} with params={params}")
        response = session.get(url, params=params, timeout=30, verify=False)
        response.raise_for_status()
        data = response.json()
        print(f"[DEBUG] API 응답 성공: 상태 코드 {response.status_code}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request error in get_real_estate_data_api: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred in get_real_estate_data_api: {e}")
        raise

def process_data_api(data):
    if not data:
        print("[DEBUG] 처리할 데이터 없음")
        return []
    articles = data.get('articleList', [])
    if not articles:
        print("[DEBUG] articleList가 비어 있음")
    processed_data = []
    for article in articles:
        tags = ', '.join(article.get('tagList', [])) if article.get('tagList') else ''
        processed_article = {
            '순번': 'N/A', # This will be filled on the client side or removed if not needed
            '아파트명': article.get('articleName'),
            '거래유형': article.get('tradeTypeName'),
            '층수': article.get('floorInfo'),
            '월세': article.get('rentPrc'),
            '거래가격': article.get('dealOrWarrantPrc'),
            '면적(m²)' : article.get('area2'),
            '방향': article.get('direction'),
            '등록일': article.get('articleConfirmYmd'),
            '동': article.get('buildingName'),
            '중개사무소': article.get('realtorName'),
            '특징': tags
        }
        processed_data.append(processed_article)
    print(f"[DEBUG] 처리된 매물 수: {len(processed_data)}")
    return processed_data

def fetch_all_pages_api(complex_no, trade_type):
    all_data = []
    page = 1
    while True:
        response_data = get_real_estate_data_api(complex_no, trade_type, page)
        if not response_data or not response_data.get('articleList'):
            print(f"[DEBUG] 페이지 {page}에서 데이터 없음 또는 articleList 비어 있음")
            break
        processed_data = process_data_api(response_data)
        all_data.extend(processed_data)
        if not response_data.get('isMoreData', False):
            print(f"[DEBUG] 더 이상 데이터 없음")
            break
        page += 1
        time.sleep(1) # Add a small delay to avoid overwhelming the server
    all_data.sort(key=lambda x: x['등록일'] if x['등록일'] else '99999999')
    return all_data

# ------------------------ API 엔드포인트 ------------------------ #
@app.route('/api/search_region', methods=['GET'])
def search_region_endpoint():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400
    try:
        complexes = get_complexes_by_region_api(keyword)
        if not complexes:
            return jsonify({"message": "No complexes found for the given keyword"}), 200
        return jsonify(complexes), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch data from Naver: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/get_real_estate_data', methods=['GET'])
def get_real_estate_data_endpoint():
    complex_no = request.args.get('complex_no')
    trade_type_display = request.args.get('trade_type')

    if not complex_no or not trade_type_display:
        return jsonify({"error": "complex_no and trade_type are required"}), 400

    trade_type = TRADE_TYPE_MAPPING.get(trade_type_display)
    if trade_type is None:
        return jsonify({"error": "Invalid trade_type"}), 400

    try:
        all_data = fetch_all_pages_api(complex_no, trade_type)
        if not all_data:
            return jsonify({"message": "No real estate data found for the given criteria"}), 200
        return jsonify(all_data), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch data from Naver: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/')
def home():
    return "Naver Real Estate API is running!"

if __name__ == '__main__':
    app.run(debug=True)
