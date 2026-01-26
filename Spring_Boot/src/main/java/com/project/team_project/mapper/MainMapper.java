package com.project.team_project.mapper;

import com.project.team_project.domain.SeoulDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface MainMapper {

    // INSERT
    int insertAllSeoulData(List<SeoulDTO> dataList);

    // SELECT
    List<SeoulDTO> selectAllSeoulData();

    Long selectSeoulDataByCondition();

    List<SeoulDTO> selectSeoulDataByIndustry(@Param("sectorName") String industry);

    // UPDATE
    int updateSeoulData(SeoulDTO seoulDTO);

    int updateAllSeoulData(List<SeoulDTO> list);


    //PAGING
    List<SeoulDTO> selectSeoulDataPaging(
            @Param("size") int size,
            @Param("offset") int offset
    );

    int countSeoulData();
}
