package com.project.team_project.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataAccessException;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.client.RestClientException;

@Slf4j
@ControllerAdvice
public class GlobalExceptionHandler {
    /* 익셉션 처리 */

    @ExceptionHandler(DataAccessException.class)
    public String handleDb(Exception e, Model model) {
        /* DB 관련 익셉션 처리 */
        log.error("[EXCEPT][DB] ", e);
        model.addAttribute("errorMsg", "DB 처리 중 문제 발생.");
        return "error";
    }

    @ExceptionHandler(RestClientException.class)
    public String handleFlask(Exception e, Model model) {
        /* Flask 서버 관련 익셉션 처리 */
        log.error("[EXCEPT][FLASK] ", e);
        model.addAttribute("errorMsg", "Flask 서버와 통신실패");
        return "error";
    }

    @ExceptionHandler(Exception.class)
    public  String handleException(Exception e,Model model){
        /* 기타 익셉션 처리 */
        log.error("[EXCEPT][ETC]",e);
        model.addAttribute("errorMsg","기타 문제 발생");
        return  "error";
    }
}
