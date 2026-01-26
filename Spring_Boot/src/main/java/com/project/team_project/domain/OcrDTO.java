package com.project.team_project.domain;

import lombok.Data;

import java.util.List;

@Data
public class OcrDTO {
    //받아온 OCR 데이터
    private List<String> lines;
}
