document.addEventListener('DOMContentLoaded', () => {
    const regionInput = document.getElementById('region-input');
    const searchRegionBtn = document.getElementById('search-region-btn');
    const complexSelect = document.getElementById('complex-select');
    const tradeTypeSelect = document.getElementById('trade-type-select');
    const startCrawlingBtn = document.getElementById('start-crawling-btn');
    const statusMessage = document.getElementById('status-message');
    const dataTableBody = document.querySelector('#data-table tbody');

    let complexesData = []; // To store complexNo along with complexName

    // Function to update status message
    const updateStatus = (message, isError = false) => {
        statusMessage.textContent = message;
        statusMessage.style.color = isError ? '#E76F51' : '#457B9D';
    };

    // Event listener for Region Search button
    searchRegionBtn.addEventListener('click', async () => {
        const keyword = regionInput.value.trim();
        if (!keyword) {
            updateStatus('지역명을 입력하세요.', true);
            return;
        }

        updateStatus('지역 검색 중...');
        complexSelect.innerHTML = '<option value="">단지를 선택하세요</option>';
        complexSelect.disabled = true;
        complexesData = [];

        try {
            const response = await fetch(`/api/search_region?keyword=${keyword}`);
            const data = await response.json();

            if (response.ok) {
                if (data.length > 0) {
                    complexesData = data;
                    data.forEach(complex => {
                        const option = document.createElement('option');
                        option.value = complex.complexNo;
                        option.textContent = `${complex.complexName} (${complex.complexNo})`;
                        complexSelect.appendChild(option);
                    });
                    complexSelect.disabled = false;
                    updateStatus(`${data.length}개의 단지를 찾았습니다.`);
                } else {
                    updateStatus('해당 지역에 단지가 없습니다.', true);
                }
            } else {
                updateStatus(`오류: ${data.error || '알 수 없는 오류'}`, true);
            }
        } catch (error) {
            updateStatus(`네트워크 오류: ${error.message}`, true);
        }
    });

    // Event listener for Start Crawling button
    startCrawlingBtn.addEventListener('click', async () => {
        const selectedComplexNo = complexSelect.value;
        const selectedTradeType = tradeTypeSelect.value;

        if (!selectedComplexNo) {
            updateStatus('단지를 선택하세요.', true);
            return;
        }

        updateStatus('데이터 수집 시작...');
        startCrawlingBtn.disabled = true;
        dataTableBody.innerHTML = ''; // Clear previous results

        try {
            const response = await fetch(`/api/get_real_estate_data?complex_no=${selectedComplexNo}&trade_type=${selectedTradeType}`);
            const data = await response.json();

            if (response.ok) {
                if (data.length > 0) {
                    updateStatus(`총 ${data.length}개의 매물을 수집했습니다.`);
                    data.forEach((item, index) => {
                        const row = dataTableBody.insertRow();
                        row.insertCell().textContent = index + 1; // 순번
                        row.insertCell().textContent = item['아파트명'];
                        row.insertCell().textContent = item['거래유형'];
                        row.insertCell().textContent = item['층수'];
                        row.insertCell().textContent = item['월세'];
                        row.insertCell().textContent = item['거래가격'];
                        row.insertCell().textContent = item['면적(m²)'];
                        row.insertCell().textContent = item['방향'];
                        row.insertCell().textContent = item['등록일'];
                        row.insertCell().textContent = item['동'];
                        row.insertCell().textContent = item['중개사무소'];
                        row.insertCell().textContent = item['특징'];
                    });
                } else {
                    updateStatus('수집된 데이터가 없습니다.');
                }
            } else {
                updateStatus(`오류: ${data.error || '알 수 없는 오류'}`, true);
            }
        } catch (error) {
            updateStatus(`네트워크 오류: ${error.message}`, true);
        } finally {
            startCrawlingBtn.disabled = false;
        }
    });
});
