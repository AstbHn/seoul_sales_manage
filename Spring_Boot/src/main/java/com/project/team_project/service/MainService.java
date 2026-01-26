package com.project.team_project.service;

import com.project.team_project.domain.OcrDTO;
import com.project.team_project.domain.PredictDTO;
import com.project.team_project.domain.SeoulDTO;
import com.project.team_project.mapper.MainMapper;
import com.project.team_project.util.MultipartInputStreamFileResource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.text.DecimalFormat;
import java.time.LocalDate;
import java.util.*;


@Slf4j
@Service
public class MainService {

    @Autowired
    MainMapper mapper;
    @Autowired
    RestTemplate rest;

    //Flask 서버 주소
    private static final String FLASK_URL = "http://localhost:5678/";

    /* 허용 업종 (CSV / JSON 유효성 검사 기준) */
    private static final Set<String> VALID_SECTORS = Set.of(
            "한식음식점", "일식음식점", "양식음식점", "중식음식점", "패스트푸드점"
    );

    /* ======================
       Startup 관련 처리
       ====================== */

    public void initDatabaseIfEmpty() {
        //초기 DB 값이 없을 경우 RPA를 통해 받아놓은 CSV 데이터 삽입
        log.info("[Database] Checking database state");

        if (selectSeoulDataByCondition() > 0) {
            log.info("[Database] data exists");
            return;
        }

        log.warn("[Database] No data found - init from Flask");

        List<Map<String, Object>> data =
                rest.getForObject(FLASK_URL + "init_program", List.class);

        if (data == null || data.isEmpty()) {
            log.error("[Startup] Flask returned no data");
            return;
        }

        List<SeoulDTO> dtoList = convertOnly(data);

        int cnt = insertAllSeoulData(dtoList);
        log.info("[Database] insert data count={}", cnt);
    }

    public void trainModelsAtStartup() {
        //초기 모델 생성
        log.info("[Startup] Training ML models via Flask");

        List<SeoulDTO> allData = selectAllSeoulData();

        if (allData == null || allData.isEmpty()) {
            log.warn("[Startup] No data to train models");
            return;
        }

        //DTO -> payload
        rest.postForEntity(
                FLASK_URL + "sklearn_run",
                toTrainPayload(allData),
                Void.class
        );

        log.info("[Startup] Model training request sent");
    }

    /* ======================
       DB
       ====================== */
    public Long selectSeoulDataByCondition() {
        return mapper.selectSeoulDataByCondition();
    }

    public int insertAllSeoulData(List<SeoulDTO> list) {
        int result = mapper.insertAllSeoulData(list);
        log.info("[DB][INSERT] inserted rows={}", result);
        return result;
    }

    public List<SeoulDTO> selectAllSeoulData() {
        return mapper.selectAllSeoulData();
    }

    public List<SeoulDTO> selectSeoulDataPaging(int page, int size) {
        int offset = (page - 1) * size;
        return mapper.selectSeoulDataPaging(size, offset);
    }

    public int countSeoulData() {
        return mapper.countSeoulData();
    }

    public List<SeoulDTO> selectSeoulDataByIndustry(String industry) {
        return mapper.selectSeoulDataByIndustry(industry);
    }

    public int updateAllSeoulData(List<SeoulDTO> list) {
        return mapper.updateAllSeoulData(list);
    }

    public int updateSeoulData(SeoulDTO dto) {
        int updated = mapper.updateSeoulData(dto);

        if (updated == 0) {
            log.warn("[DB][UPDATE] no rows affected | {}", dto);
        }
        return updated;
    }


    /* ======================
       CSV / JSON 처리
       ====================== */

    public List<Map<String, Object>> sendCsvToFlask(MultipartFile file) {
        /* CSV 파일 Flask 전송 */
        return sendFileToFlask(file, "read_csv");
    }

    public List<Map<String, Object>> sendJsonToFlask(MultipartFile file) {
        /* JSON 파일 Flask 전송 */
        return sendFileToFlask(file, "read_json");
    }

    private List<Map<String, Object>> sendFileToFlask(MultipartFile file, String path) {
        /* Multipart 파일 공통 Flask 전송 로직 */
        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new MultipartInputStreamFileResource(file));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            return rest.postForObject(
                    FLASK_URL + path,
                    new HttpEntity<>(body, headers),
                    List.class
            );
        } catch (IOException e) {
            throw new RuntimeException("Flask 파일 전송 실패", e);
        }
    }

    public List<SeoulDTO> validateAndConvert(List<Map<String, Object>> data) {
        /* CSV 유효성 검사 + DTO 변환 */
        int currentYear = LocalDate.now().getYear();

        log.info("[VALIDATE][CSV] raw rows={}", data.size());

        List<SeoulDTO> result = data.stream()
                .filter(map -> {
                    Object y = map.get("연도");
                    Object q = map.get("분기");
                    Object s = map.get("업종");

                    boolean valid =
                            y instanceof Integer year &&
                                    q instanceof Integer quarter &&
                                    s instanceof String sector &&
                                    year >= 2019 && year <= currentYear &&
                                    quarter >= 1 && quarter <= 4 &&
                                    VALID_SECTORS.contains(sector);

                    if (!valid) {
                        log.warn("[VALIDATE][CSV][DROP] 연도={}({}), 분기={}({}), 업종={}({})",
                                y, (y == null ? "null" : y.getClass().getSimpleName()),
                                q, (q == null ? "null" : q.getClass().getSimpleName()),
                                s, (s == null ? "null" : s.getClass().getSimpleName())
                        );
                    }
                    return valid;
                })
                .map(this::mapToDto)
                .toList();

        log.info("[VALIDATE][CSV] valid rows={}", result.size());
        return result;
    }

    public List<SeoulDTO> validateAndConvertJson(List<Map<String, Object>> data) {
        /* JSON 유효성 검사 + DTO 변환 */
        int currentYear = LocalDate.now().getYear();

        return data.stream()
                .filter(map ->
                        map.get("연도") instanceof Integer year &&
                                map.get("분기") instanceof Integer quarter &&
                                map.get("업종") instanceof String sector &&
                                year >= 2019 && year <= currentYear &&
                                quarter >= 1 && quarter <= 4 &&
                                VALID_SECTORS.contains(sector)
                )
                .map(this::mapToDto)
                .toList();
    }

    public List<SeoulDTO> convertOnly(List<Map<String, Object>> data) {
        /* 초기 적재/신뢰 데이터용 변환 */
        return data.stream().map(this::mapToDto).toList();
    }

    private SeoulDTO mapToDto(Map<String, Object> map) {
        //Map 형식으로 된 데이터를 DTO 형태로 수정
        SeoulDTO dto = new SeoulDTO();
        dto.setSectorName((String) map.get("업종"));
        dto.setYear((Integer) map.get("연도"));
        dto.setQuarter((Integer) map.get("분기"));
        dto.setSalesAmount(((Number) map.get("매출액")).longValue());
        dto.setSalesCount(((Number) map.get("매출건수")).longValue());
        return dto;
    }


    /* ======================
       예측 / OCR
       ====================== */

    public Map<String, Object> requestPrediction(PredictDTO dto) {

        Map<String, Object> body = Map.of(
                "year", dto.getYear(),
                "quarter", dto.getQuarter(),
                "sector_name", dto.getSectorName()
        );

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, Object> result =
                rest.postForObject(
                        FLASK_URL + "sklearn_predict",
                        new HttpEntity<>(body, headers),
                        Map.class
                );

        if (result == null) {
            log.error("[PREDICT] Flask returned null | sector={}, year={}, quarter={}",
                    dto.getSectorName(), dto.getYear(), dto.getQuarter());
            return null;
        }

        // 숫자 포맷 (화면 출력용)
        long amount = ((Number) result.get("pred_sales_amount")).longValue();
        long count = ((Number) result.get("pred_sales_count")).longValue();

        DecimalFormat df = new DecimalFormat("#,###");
        result.put("pred_sales_amount_fmt", df.format(amount));
        result.put("pred_sales_count_fmt", df.format(count));

        result.putIfAbsent("year", dto.getYear());
        result.putIfAbsent("quarter", dto.getQuarter());
        result.putIfAbsent("sector_name", dto.getSectorName());

        return result;
    }

    public SeoulDTO buildPredRow(PredictDTO req, Map<String, Object> predResult) {
        /* 예측 결과를 차트ㆍ리포트에 붙이기 위한 DTO 생성 */
        SeoulDTO pred = new SeoulDTO();
        pred.setSectorName(req.getSectorName());
        pred.setYear(req.getYear());
        pred.setQuarter(req.getQuarter());
        pred.setSalesAmount(((Number) predResult.get("pred_sales_amount")).longValue());
        pred.setSalesCount(((Number) predResult.get("pred_sales_count")).longValue());
        return pred;
    }

    public int processOcr(OcrDTO dto) {
        SeoulDTO seoulDTO = ocrDTOToSeoulDTO(dto.getLines());
        int updated = updateSeoulData(seoulDTO);

        if (updated > 0) {
            update_single(seoulDTO.getSectorName());
        }
        return updated;
    }

    public SeoulDTO ocrDTOToSeoulDTO(List<String> lines) {
        SeoulDTO dto = new SeoulDTO();

        for (String line : lines) {
            String[] parts = line.split(":");
            if (parts.length != 2) continue;

            switch (parts[0].trim()) {
                case "연도" -> dto.setYear(Integer.parseInt(parts[1].trim()));
                case "분기" -> dto.setQuarter(Integer.parseInt(parts[1].trim()));
                case "업종" -> dto.setSectorName(parts[1].trim());
                case "매출액" -> dto.setSalesAmount(Long.parseLong(parts[1].trim()));
                case "매출건수" -> dto.setSalesCount(Long.parseLong(parts[1].trim()));
            }
        }
        return dto;
    }

    /* ======================
       차트 / PDF / 재학습
       ====================== */

    public Map<String, Object> getChartData() {
        /* 전체 데이터 기반 차트 (viewpage 등 공용) */
        return rest.postForObject(
                FLASK_URL + "chart_data",
                Map.of("rows", selectAllSeoulData()),
                Map.class
        );
    }

    public Map<String, Object> getPredictChartData(List<SeoulDTO> rows, SeoulDTO predRow) {
        /* 예측 페이지 전용 차트:
           - rows      : 업종별 과거 데이터(실선)
           - pred_rows : 예측값 1건(점선)
         */
        Map<String, Object> body = new HashMap<>();
        body.put("rows", rows);
        body.put("pred_rows", List.of(predRow));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        return rest.postForObject(
                FLASK_URL + "chart_data",
                new HttpEntity<>(body, headers),
                Map.class
        );
    }

    public void requestCreatePdf(List<SeoulDTO> rows, SeoulDTO predRow) {
        /* PDF 다운로드 기능 유지용:
           - Flask에서 예측 보고서 PDF 생성
         */
        List<SeoulDTO> pdfRows = new ArrayList<>(rows);
        pdfRows.add(predRow);

        Map<String, Object> body = new HashMap<>();
        body.put("rows", pdfRows);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        try {
            rest.postForEntity(
                    FLASK_URL + "create_pdf",
                    new HttpEntity<>(body, headers),
                    String.class
            );
            log.info("[PDF] create_pdf request sent");
        } catch (Exception e) {
            // PDF는 “부가 기능”이라 실패해도 예측 자체는 보여주게 처리
            log.warn("[PDF] create_pdf failed: {}", e.getMessage());
        }
    }

    public void updateSl() {
        /* CSV/JSON 업데이트 후 전체 모델 재학습 */
        List<SeoulDTO> allData = selectAllSeoulData();
        if (allData == null || allData.isEmpty()) {
            log.warn("[SKLEARN] No data found. Skip training.");
            return;
        }

        rest.postForEntity(
                FLASK_URL + "sklearn_run",
                toTrainPayload(allData),
                Void.class
        );
        log.info("[SKLEARN] Model training request success");
    }

    public void update_single(String sectorName) {
        log.info("[SKLEARN] Retrain single sector: {}", sectorName);

        List<SeoulDTO> allData = selectAllSeoulData();
        if (allData == null || allData.isEmpty()) {
            log.warn("[SKLEARN] No data found. Skip single retrain.");
            return;
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        rest.postForEntity(
                FLASK_URL + "sklearn_run_single?category_name=" + sectorName,
                new HttpEntity<>(toTrainPayload(allData), headers),
                Void.class
        );

        log.info("[SKLEARN] Single sector retrain success: {}", sectorName);
    }

    private List<Map<String, Object>> toTrainPayload(List<SeoulDTO> rows) {
        /* DTO 를 MAP 형식으로 변환 */
        return rows.stream()
                .map(dto -> {
                    Map<String, Object> m = new HashMap<>();
                    m.put("year", dto.getYear());
                    m.put("quarter", dto.getQuarter());
                    m.put("sector_name", dto.getSectorName());
                    m.put("sales_amount", dto.getSalesAmount());
                    m.put("sales_count", dto.getSalesCount());
                    return m;
                })
                .toList();
    }
}
