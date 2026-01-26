package com.project.team_project.domain;

import lombok.Data;

@Data
public class PredictDTO {
    //예측 값
    private int year;            // 연도
    private int quarter;         // 분기
    private String sectorName;   // 업종명
}
