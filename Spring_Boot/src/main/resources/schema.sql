CREATE TABLE IF NOT EXISTS team1table (
    year INT NOT NULL,
    quarter INT NOT NULL,
    sector_name VARCHAR(100) NOT NULL,
    sales_amount BIGINT NOT NULL,
    sales_count BIGINT NOT NULL,

    -- 중복 판단 기준
    UNIQUE KEY uk_sector_year_quarter (sector_name, year, quarter)
);
