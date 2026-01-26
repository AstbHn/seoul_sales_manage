/* =========================
   Google Analytics (GA4)
========================= */
window.dataLayer = window.dataLayer || [];
function gtag() {
    dataLayer.push(arguments);
}

// GA 시작
gtag('js', new Date());

// 기본 페이지뷰
gtag('config', 'G-52F6BP6M76');

/* =========================
   공통 이벤트
========================= */

// 다운로드
function trackDownload(type) {
    gtag('event', 'file_download', {
        event_category: 'download',
        event_label: type,
        file_type: type
    });
}

// CSV 업로드
function trackCsvUpload() {
    gtag('event', 'upload_csv', {
        event_category: 'data',
        event_label: 'csv_upload'
    });
}

// JSON 업로드
function trackJsonUpload() {
    gtag('event', 'upload_json', {
        event_category: 'data',
        event_label: 'json_upload'
    });
}

// 예측 실행
function trackPredict(sector) {
    gtag('event', 'predict_run', {
        event_category: 'prediction',
        event_label: sector
    });
}

// 페이지 이동
function trackPage(pageName) {
    gtag('event', 'page_move', {
        event_category: 'navigation',
        event_label: pageName
    });
}
