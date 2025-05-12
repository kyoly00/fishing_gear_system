import React, { useState, useMemo, useEffect, useCallback } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import './Report.css';

const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);
const CAST_TYPES = ['자망', '통발', '근해자망', '연안자망'];
const CAST_COLORS = ['#1f3d75', '#3d75a3', '#75a3bf', '#a3bfdf'];

const reports = Array.from({ length: 40 }, (_, idx) => {
  const report_id = idx + 1;
  const month = (idx % 12) + 1;
  const day = (idx % 28) + 1;
  const pad = n => String(n).padStart(2, '0');
  return {
    report_id,
    lg_buyer_id: 200000 + report_id,
    lg_admin_id: 20100000 + ((idx % 5) + 1),
    cast_latitude: +(33.5 + month * 0.1).toFixed(6),
    cast_longitude: +(126.0 + month * 0.15).toFixed(6),
    cast_time: `2025-${pad(month)}-${pad(day)} 08:00:00`,
    report_time: `2025-${pad(month)}-${pad(day)} 14:00:00`,
    cast_type: CAST_TYPES[idx % CAST_TYPES.length]
  };
});

export default function ReportDB() {
  const [filterMonth, setFilterMonth] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    setCurrentPage(1);
  }, [filterMonth]);

  const monthlyData = useMemo(
    () =>
      MONTHS.map(m => ({
        month: `${m}월`,
        count: reports.filter(r => new Date(r.cast_time).getMonth() + 1 === m).length
      })),
    []
  );

  const overallCollectData = useMemo(() => {
    const o = Math.floor(Math.random() * 101);
    return [
      { name: '수거 O', value: o, color: '#82ca9d' },
      { name: '수거 X', value: 100 - o, color: '#ff7f50' }
    ];
  }, []);

  const filteredReports = useMemo(
    () =>
      filterMonth
        ? reports.filter(r => new Date(r.cast_time).getMonth() + 1 === filterMonth)
        : reports,
    [filterMonth]
  );

  const totalPages = Math.ceil(filteredReports.length / itemsPerPage);
  const startIdx = (currentPage - 1) * itemsPerPage;
  const currentReports = filteredReports.slice(startIdx, startIdx + itemsPerPage);

  const pieData = useMemo(() => {
    if (filterMonth == null) return [];
    const counts = {};
    filteredReports.forEach(r => {
      counts[r.cast_type] = (counts[r.cast_type] || 0) + 1;
    });
    return CAST_TYPES.map((type, i) => ({
      name: type,
      value: counts[type] || 0,
      color: CAST_COLORS[i]
    }));
  }, [filterMonth, filteredReports]);

  const collectData = useMemo(() => {
    if (filterMonth == null) return [];
    const o = Math.floor(Math.random() * 101);
    return [
      { name: '수거 O', value: o, color: '#82ca9d' },
      { name: '수거 X', value: 100 - o, color: '#ff7f50' }
    ];
  }, [filterMonth]);

  const handleFilter = useCallback(m => {
    setFilterMonth(prev => (prev === m ? null : m));
  }, []);

  return (
    <div className="buyerdb-container">
      <h2>신고자 정보 리스트</h2>

      <div className="month-filters">
        <button className={filterMonth === null ? 'active' : ''} onClick={() => handleFilter(null)}>
          전체
        </button>
        {MONTHS.map(m => (
          <button
            key={m}
            className={filterMonth === m ? 'active' : ''}
            onClick={() => handleFilter(m)}
          >
            {m}월
          </button>
        ))}
      </div>

      <div className="table-section">
        <table className="buyer-table">
          <thead>
            <tr>
              <th>신고 ID</th>
              <th>구매자 ID</th>
              <th>관리자 ID</th>
              <th>위도</th>
              <th>경도</th>
              <th>투망 시간</th>
              <th>신고 시간</th>
              <th>투망 종류</th>
            </tr>
          </thead>
          <tbody>
            {currentReports.map(r => (
              <tr key={r.report_id}>
                <td>{r.report_id}</td>
                <td>{r.lg_buyer_id}</td>
                <td>{r.lg_admin_id}</td>
                <td>{r.cast_latitude}</td>
                <td>{r.cast_longitude}</td>
                <td>{r.cast_time}</td>
                <td>{r.report_time}</td>
                <td>{r.cast_type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button disabled={currentPage === 1} onClick={() => setCurrentPage(p => Math.max(p - 1, 1))}>
          이전
        </button>
        {[...Array(totalPages)].map((_, i) => (
          <button
            key={i}
            className={currentPage === i + 1 ? 'active' : ''}
            onClick={() => setCurrentPage(i + 1)}
          >
            {i + 1}
          </button>
        ))}
        <button
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))}
        >
          다음
        </button>
      </div>

      <div className="chart-section">
        {filterMonth == null ? (
          <div style={{ display: 'flex', gap: 20 }}>
            <div style={{ flex: 3 }}>
              <h3>월별 신고량</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={monthlyData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1f3d75" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={{ flex: 2 }}>
              <h3>전체 수거율</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={overallCollectData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {overallCollectData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.color} />
                    ))}
                  </Pie>
                  <Legend verticalAlign="bottom" height={36} />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div className="pie-charts" style={{ display: 'flex', gap: 20 }}>
            <div className="pie-chart-item">
              <h3>어구 종류별 신고량</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {pieData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.color} />
                    ))}
                  </Pie>
                  <Legend verticalAlign="bottom" height={36} />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="pie-chart-item">
              <h3>수거율</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={collectData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {collectData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.color} />
                    ))}
                  </Pie>
                  <Legend verticalAlign="bottom" height={36} />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}