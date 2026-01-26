package com.project.team_project.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class AppConfig {
    @Bean
    public RestTemplate restTemplate() {
        /*HTTP 요청도구 생성 후 Bean에 등록*/
        return new RestTemplate();
    }
}