package com.project.team_project.config;

import com.project.team_project.service.MainService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class StartupRunner implements ApplicationRunner {

    @Autowired
    MainService mainService;

    @Override
    public void run(ApplicationArguments args) {
        //서버가 실행 된 후
        log.info("[Startup] Application started");

        // DB 초기 데이터 확인 및 적재
        mainService.initDatabaseIfEmpty();

        // Flask ML 모델 초기 학습
        mainService.trainModelsAtStartup();
    }
}
