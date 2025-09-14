document.addEventListener('DOMContentLoaded', function() {
    // 지역 검색 버튼 클릭 이벤트
    document.getElementById('searchRegion').addEventListener('click', function() {
        const region = document.getElementById('region').value.trim();
        if (!region) {
            alert('지역명을 입력하세요.');
            return;
        }

        const formData = new FormData();
        formData.append('keyword', region);

        fetch('/search', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            const complexSelect = document.getElementById('complex');
            complexSelect.innerHTML = '<option value="">단지를 선택하세요</option>';
            
            data.complexes.forEach(complex => {
                const option = document.createElement('option');
                option.value = complex.complexNo;
                option.textContent = `${complex.complexName} (${complex.complexNo})`;
                complexSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('검색 중 오류가 발생했습니다.');
        });
    });

    // 데이터 수집 시작 버튼 클릭 이벤트
    document.getElementById('fetchData').addEventListener('click', function() {
        const complexSelect = document.getElementById('complex');
        const tradeTypeSelect = document.getElementById('tradeType');
        
        if (!complexSelect.value) {
            alert('아파트 단지를 선택하세요.');
            return;
        }

        const formData = new FormData();
        formData.append('complex_no', complexSelect.value);
        formData.append('trade_type', tradeTypeSelect.value);

        // 로딩 모달 표시
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();

        fetch('/fetch_data', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingModal.hide();
            
            if (data.error) {
                alert(data.error);
                return;
            }

            // 테이블 업데이트
            const tbody = document.querySelector('#dataTable tbody');
            tbody.innerHTML = '';
            
            data.data.forEach((item, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${item['아파트명'] || ''}</td>
                    <td>${item['거래유형'] || ''}</td>
                    <td>${item['층수'] || ''}</td>
                    <td>${item['월세'] || ''}</td>
                    <td>${item['거래가격'] || ''}</td>
                    <td>${item['면적(m²)'] || ''}</td>
                    <td>${item['방향'] || ''}</td>
                    <td>${item['등록일'] || ''}</td>
                    <td>${item['동'] || ''}</td>
                    <td>${item['중개사무소'] || ''}</td>
                    <td>${item['특징'] || ''}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            loadingModal.hide();
            console.error('Error:', error);
            alert('데이터 수집 중 오류가 발생했습니다.');
        });
    });

    // 엑셀 다운로드 버튼 클릭 이벤트
    document.getElementById('downloadExcel').addEventListener('click', function() {
        const rows = Array.from(document.querySelectorAll('#dataTable tbody tr'));
        if (rows.length === 0) {
            alert('다운로드할 데이터가 없습니다.');
            return;
        }

        const data = rows.map(row => {
            const cells = Array.from(row.cells);
            return {
                '순번': cells[0].textContent,
                '아파트명': cells[1].textContent,
                '거래유형': cells[2].textContent,
                '층수': cells[3].textContent,
                '월세': cells[4].textContent,
                '거래가격': cells[5].textContent,
                '면적(m²)': cells[6].textContent,
                '방향': cells[7].textContent,
                '등록일': cells[8].textContent,
                '동': cells[9].textContent,
                '중개사무소': cells[10].textContent,
                '특징': cells[11].textContent
            };
        });

        fetch('/download_excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data: data })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'real_estate_data.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('엑셀 다운로드 중 오류가 발생했습니다.');
        });
    });
}); 