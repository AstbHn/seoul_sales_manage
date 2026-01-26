package com.project.team_project.domain;

import lombok.Data;

@Data
public class SeoulDTO {
    //기본적인 데이터
    private int year;            // 연도
    private int quarter;         // 분기
    private String sectorName;   // 업종명
    private Long salesAmount;    // 매출액
    private Long salesCount;     // 매출건수
}
