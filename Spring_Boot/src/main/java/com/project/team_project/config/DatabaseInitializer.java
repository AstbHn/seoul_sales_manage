package com.project.team_project.config;

import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

@Component
public class DatabaseInitializer {
    @PostConstruct
    public void init() throws Exception {
        /*서버실행하면서 데이터베이스 생성*/
        Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/?serverTimezone=UTC",
                "root",
                "1234"
        );

        Statement stmt = conn.createStatement();
        stmt.executeUpdate("CREATE DATABASE IF NOT EXISTS team1DB");

        stmt.close();
        conn.close();
    }
}

