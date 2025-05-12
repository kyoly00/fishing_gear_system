// src/pages/BuyerDB.js
import React, { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import "./BuyerDB.css";

const months = [
  "전체","1월","2월","3월","4월","5월",
  "6월","7월","8월","9월","10월","11월","12월",
];

// 더미 데이터 20개
const buyers = [
  { name: "이병호", gearId: "30b710849", location: "경남 남해군 미조면 미조로 89", type: "자망",    contact: "010-2811-9617", date: "2024-01-15" },
  { name: "정도현", gearId: "59t104762", location: "경남 남해군 미조면 미조로 89", type: "통발",    contact: "010-5908-8374", date: "2024-02-08" },
  { name: "임정숙", gearId: "65v805637", location: "경남 남해군 미조면 미조로 89", type: "통발",    contact: "010-1536-5207", date: "2024-03-12" },
  { name: "강용준", gearId: "72f529856", location: "경남 남해군 미조면 미조로 89", type: "자망",    contact: "010-8414-3165", date: "2024-04-22" },
  { name: "박기석", gearId: "11q766761", location: "경남 남해군 설천면 설천로 78", type: "통발",    contact: "010-3272-9404", date: "2024-05-30" },
  { name: "이병호", gearId: "30q572408", location: "경남 남해군 설천면 설천로 78", type: "통발",    contact: "010-4142-6642", date: "2024-06-18" },
  { name: "정성호", gearId: "44j837798", location: "경남 남해군 설천면 설천로 78", type: "자망",    contact: "010-8169-9673", date: "2024-07-03" },
  { name: "임철수", gearId: "60w115253", location: "경남 남해군 설천면 설천로 78", type: "자망",    contact: "010-8420-4071", date: "2024-08-25" },
  { name: "최철수", gearId: "20u067685", location: "경남 남해군 창선면 지죽로 134", type: "자망",   contact: "010-8250-2544", date: "2024-09-17" },
  { name: "강성호", gearId: "56o940976", location: "경남 남해군 창선면 지죽로 134", type: "자망",   contact: "010-4397-1370", date: "2024-10-09" },
  { name: "윤미영", gearId: "79l755401", location: "경남 남해군 창선면 지죽로 134", type: "자망",   contact: "010-8785-4333", date: "2024-11-14" },
  { name: "정성호", gearId: "60b087480", location: "경남 남해군 남면 당항로 75",    type: "자망",    contact: "010-2239-9077", date: "2024-12-02" },
  { name: "김소윤", gearId: "85z112233", location: "경남 남해군 이동면 중촌로 45", type: "통발",    contact: "010-1234-5678", date: "2024-01-28" },
  { name: "김태리", gearId: "22y445566", location: "경남 남해군 이동면 중촌로 45", type: "근해자망", contact: "010-9876-5432", date: "2024-02-19" },
  { name: "박보검", gearId: "13x998877", location: "경남 남해군 이동면 중촌로 45", type: "연안자망", contact: "010-5555-6666", date: "2024-03-05" },
  { name: "한지민", gearId: "49w223344", location: "경남 남해군 이동면 중촌로 45", type: "통발",    contact: "010-1111-2222", date: "2024-04-16" },
  { name: "문채원", gearId: "77u334455", location: "경남 남해군 이동면 중촌로 45", type: "연안자망", contact: "010-3333-4444", date: "2024-05-07" },
  { name: "정우성", gearId: "88t556677", location: "경남 남해군 이동면 중촌로 45", type: "근해자망", contact: "010-7777-8888", date: "2024-06-29" },
  { name: "이민호", gearId: "66s778899", location: "경남 남해군 이동면 중촌로 45", type: "근해자망", contact: "010-0000-1111", date: "2024-07-21" },
  { name: "박신혜", gearId: "55r889900", location: "경남 남해군 이동면 중촌로 45", type: "연안자망", contact: "010-9090-8080", date: "2024-08-11" },
];

export default function BuyerDB() {
  const [filterMonth, setFilterMonth] = useState("전체");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  // -- 테이블: filterMonth 에 따라 필터링 --
  const tableData =
    filterMonth === "전체"
      ? buyers
      : buyers.filter(
          (b) =>
            new Date(b.date).getMonth() + 1 ===
            Number(filterMonth.replace("월", ""))
        );

  const totalPages = Math.ceil(tableData.length / itemsPerPage);
  const startIdx = (currentPage - 1) * itemsPerPage;
  const currentBuyers = tableData.slice(startIdx, startIdx + itemsPerPage);
  const goToPage = (n) => setCurrentPage(n);

  // 어구 종류 & 색상
  const gearTypes = Array.from(new Set(buyers.map((b) => b.type)));
  const colorMap = {
    자망: "#1f3d75",
    통발: "#82ca9d",
    근해자망: "#ff6961",
    연안자망: "#ffc107",
  };

  // 월별 누적 집계 (전체 모드 꺾은선용)
  const aggregatedData = months
    .slice(1)
    .map((m, idx) => {
      const monthNum = idx + 1;
      const entry = { month: m };
      gearTypes.forEach((type) => {
        entry[type] = buyers.filter(
          (b) => b.type === type && new Date(b.date).getMonth() + 1 === monthNum
        ).length;
      });
      return entry;
    });

  // 개별 월 모드 막대그래프용 (그 달 one-entry)
  const monthlyAggregated =
    filterMonth === "전체"
      ? []
      : aggregatedData.filter((e) => e.month === filterMonth);

  return (
    <div className="buyerdb-container">
      <h2>어구 구매 정보 리스트</h2>

      {/* 월별 필터 */}
      <div className="month-filters">
        {months.map((m) => (
          <button
            key={m}
            className={filterMonth === m ? "active" : ""}
            onClick={() => {
              setFilterMonth(m);
              setCurrentPage(1);
            }}
          >
            {m}
          </button>
        ))}
      </div>

      {/* ── 테이블 + 페이징 ── */}
      <div className="table-section">
        <table className="buyer-table">
          <thead>
            <tr>
              <th>구매자 이름</th>
              <th>어구 ID</th>
              <th>구매 장소</th>
              <th>구매 날짜</th>
              <th>어구 종류</th>
              <th>구매자 연락처</th>
            </tr>
          </thead>
          <tbody>
            {currentBuyers.map((b, i) => (
              <tr key={i}>
                <td>{b.name}</td>
                <td>{b.gearId}</td>
                <td>{b.location}</td>
                <td>{b.date}</td>
                <td>{b.type}</td>
                <td>{b.contact}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="pagination">
          <button
            onClick={() => goToPage(Math.max(currentPage - 1, 1))}
            disabled={currentPage === 1}
          >
            이전
          </button>
          {[...Array(totalPages)].map((_, idx) => (
            <button
              key={idx}
              className={currentPage === idx + 1 ? "active" : ""}
              onClick={() => goToPage(idx + 1)}
            >
              {idx + 1}
            </button>
          ))}
          <button
            onClick={() => goToPage(Math.min(currentPage + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            다음
          </button>
        </div>
      </div>

      {/* ── 차트 ── */}
      <div className="chart-section">
        <h3>어구별 구매량</h3>
        <ResponsiveContainer width="100%" height={400}>
          {filterMonth === "전체" ? (
            <LineChart
              data={aggregatedData}
              margin={{ top: 20, right: 20, left: 0, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              {gearTypes.map((type) => (
                <Line
                  key={type}
                  type="monotone"
                  dataKey={type}
                  name={type}
                  stroke={colorMap[type]}
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              ))}
            </LineChart>
          ) : (
            <BarChart
              data={monthlyAggregated}
              margin={{ top: 20, right: 20, left: 0, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              {gearTypes.map((type) => (
                <Bar
                  key={type}
                  dataKey={type}
                  name={type}
                  fill={colorMap[type]}
                  barSize={40}
                />
              ))}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}