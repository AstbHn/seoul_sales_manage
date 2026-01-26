package com.project.team_project.controller;

import com.project.team_project.domain.OcrDTO;
import com.project.team_project.domain.PredictDTO;
import com.project.team_project.domain.SeoulDTO;
import com.project.team_project.service.MainService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@Slf4j
@Controller
public class MainController {

    @Autowired
    MainService ms;

    /*  ======================
        Request Get
        ======================*/

    @RequestMapping({"/", "/index"})
    public String index() {
        /* 메인 페이지 이동*/
        log.info("[Controller] GET /index");
        return "index";
    }

    @GetMapping("/viewpage")
    public String viewpage(
            @RequestParam(defaultValue = "1") int page,
            Model model
    ) {
        /* 페이징 리스트 & 차트 페이지 이동 */
        log.info("[Controller] GET /viewpage | Page={}", page);

        //페이지 당 출력 개수
        int size = 10;

        model.addAttribute("dataList", ms.selectSeoulDataPaging(page, size));
        model.addAttribute("currentPage", page);

        int totalCount = ms.countSeoulData();
        int totalPages = (int) Math.ceil((double) totalCount / size);

        model.addAttribute("totalPages", totalPages);
        model.addAttribute(
                "pageList",
                java.util.stream.IntStream.rangeClosed(1, totalPages).boxed().toList()
        );

        model.addAttribute("chartDataJson", ms.getChartData());

        return "viewpage";
    }

    @GetMapping("/preview")
    public String preview() {
        /* 예측 페이지 이동 */
        log.info("[Controller] GET /preview");
        return "preview";
    }

    @GetMapping("/update_data")
    public String update_data() {
        /* 수정 페이지 이동*/
        log.info("[Controller] GET /update_data");
        return "UpdateData";
    }

    /*  ======================
        Request Post
        ======================*/

    /* 데이터 수정 수행 */
    @PostMapping("/update_to_input")
    public  String update_to_input(SeoulDTO dto){
        //사용자 입력을 통한 매출정보 수정
        log.info("[Controller] Post /update_to_input");

        ms.updateSeoulData(dto);    //DB 업데이트
        ms.update_single(dto.getSectorName()); //사이킷런 모델 재학습

        log.info("[Update]  {}",dto);
        return "redirect:/viewpage";
    }

    @PostMapping("/update_to_csv")
    public String update_to_csv(@RequestParam("csvFile") MultipartFile file) {
        //csv 파일 데이터를 이용한 매출정보 수정
        log.info("[Controller] POST /update_to_csv");

        List<Map<String, Object>> data = ms.sendCsvToFlask(file);
        List<SeoulDTO> dtoList = ms.validateAndConvert(data);

        log.info("[Controller] valid csv rows={}", dtoList.size());

        int updated = ms.updateAllSeoulData(dtoList);
        log.info("[DB] updateAllSeoulData affected rows={}", updated);

        ms.updateSl(); // 전체 재학습

        return "redirect:/viewpage";
    }

    @PostMapping("/update_to_json")
    public String update_to_json(@RequestParam("jsonFile") MultipartFile file) {
        // Json 파일 데이터를 이용한 매출정보 수정
        log.info("[Controller] POST /update_to_json");

        List<Map<String, Object>> data = ms.sendJsonToFlask(file);
        List<SeoulDTO> dtoList = ms.validateAndConvertJson(data);

        log.info("[Controller] valid json rows={}", dtoList.size());

        ms.updateAllSeoulData(dtoList);
        ms.updateSl(); // 전체 재학습

        return "redirect:/viewpage";
    }

    @PostMapping("/predict_data")
    public String predict_data(PredictDTO dto, Model model) {
        /* 데이터 예측 수행 */
        log.info("[PREDICT] request dto={}", dto);

        Map<String, Object> result = ms.requestPrediction(dto);

        if (result == null) {
            model.addAttribute("errorMsg", "예측 결과를 받아오지 못했습니다.");
            return "preview";
        }

        model.addAttribute("predict", result);

        List<SeoulDTO> dbData = ms.selectSeoulDataByIndustry(dto.getSectorName());

        SeoulDTO predRow = ms.buildPredRow(dto, result);

        Map<String, Object> predictChart = ms.getPredictChartData(dbData, predRow);
        model.addAttribute("chartDataJson", predictChart);

        ms.requestCreatePdf(dbData, predRow);

        return "preview";
    }

    @PostMapping("/ocr_result")
    public ResponseEntity<String> receiveOcr(@RequestBody OcrDTO dto) {
        /*OCR 결과 Flask로 부터 받아오기*/
        log.info("[Controller] OCR data received");

        int updated = ms.processOcr(dto);

        if (updated > 0) {
            log.info("[OCR] DB update success (rows={})", updated);
        } else {
            log.warn("[OCR] DB update failed");
        }

        return ResponseEntity.ok("OCR 저장 완료");
    }
}
