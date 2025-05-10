import React, { useEffect, useState } from 'react';
import './Dashboard.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const createCustomMarker = (index, status) => {
  const color = status === '수거완료' ? '#4caf50' : '#f44336';
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="marker-shape" style="background:${color};">
        <span class="marker-number">${index}</span>
      </div>
    `,
    iconSize: [30, 42],
    iconAnchor: [15, 42],
    popupAnchor: [0, -40],
  });
};

const Dashboard = () => {
  const [reports, setReports] = useState([]);
  const [isPanelOpen, setIsPanelOpen] = useState(true);

  useEffect(() => {
    const dummyReports = [
      { id: 1, gearType: '자망', gearId: 'FGEI08532', lat: 34.452397, lng: 127.937455, timestamp: '2025-03-18 16:03', status: '미수거' },
      { id: 2, gearType: '통발', gearId: 'FGTI00921', lat: 34.4598, lng: 127.9337, timestamp: '2025-03-18 11:10', status: '미수거' },
      { id: 3, gearType: '자망', gearId: 'FGEI12578', lat: 34.450120, lng: 127.932100, timestamp: '2025-03-18 17:40', status: '미수거' },
      { id: 4, gearType: '자망', gearId: 'FGEI84931', lat: 34.460450, lng: 127.934000, timestamp: '2025-03-18 14:03', status: '미수거' },
      { id: 5, gearType: '자망', gearId: 'FGEI08532', lat: 34.449500, lng: 127.941200, timestamp: '2025-03-18 13:30', status: '미수거' },
      { id: 6, gearType: '통발', gearId: 'FGTI23233', lat: 34.451120, lng: 127.939456, timestamp: '2025-03-18 12:00', status: '미수거' },
      { id: 7, gearType: '자망', gearId: 'FGEI85644', lat: 34.455300, lng: 127.937888, timestamp: '2025-03-18 16:50', status: '미수거' },
      { id: 8, gearType: '자망', gearId: 'FGEI08532', lat: 34.452397, lng: 127.937455, timestamp: '2025-03-18 16:03', status: '수거완료' },
      { id: 9, gearType: '통발', gearId: 'FGSK09992', lat: 34.440330, lng: 127.940000, timestamp: '2025-03-18 10:33', status: '수거완료' },
      { id: 10, gearType: '자망', gearId: 'FGEI55672', lat: 34.462000, lng: 127.942890, timestamp: '2025-03-18 17:20', status: '미수거' },
      { id: 11, gearType: '통발', gearId: 'FGTI00921', lat: 34.459800, lng: 127.933700, timestamp: '2025-03-18 11:10', status: '미수거' },
    ];
    setReports(dummyReports);
  }, []);

  const calculateElapsed = (timestamp) => {
    const now = new Date();
    const reportTime = new Date(timestamp);
    const diffMs = now - reportTime;
    const diffHours = (diffMs / (1000 * 60 * 60)).toFixed(1);
    return `유실 신고 후 ${diffHours}시간 경과`;
  };

  const togglePanel = () => setIsPanelOpen(!isPanelOpen);
  const mapCenter = [34.452397, 127.937455];

  return (
    <div className="dashboard-wrapper">
      <main className="map-section">
        <MapContainer center={mapCenter} zoom={13} style={{ width: '100%', height: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          {reports.map((r, idx) => (
            <Marker key={r.id} position={[r.lat, r.lng]} icon={createCustomMarker(idx + 1, r.status)}>
              <Popup>
                <strong>{r.gearType} ({r.gearId})</strong><br />
                {r.timestamp}<br />
                {calculateElapsed(r.timestamp)}<br />
                상태: {r.status}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </main>

      <section className={`report-list ${isPanelOpen ? 'open' : ''}`}>
        {/* ⬅ 토글 버튼을 사이드바 왼쪽에 붙임 */}
        <div className="panel-toggle-button" onClick={togglePanel}>
          {isPanelOpen ? '▶' : '◀'}
        </div>

        <div className="report-header">
          <h3>❗ 어구 신고 리스트</h3>
          <div className="status-legend">
            <div className="legend-item">
              <span className="dot green"></span>
              <span>수거선 배정 완료</span>
            </div>
            <div className="legend-item">
              <span className="dot red"></span>
              <span>수거선 배정 전</span>
            </div>
          </div>
        </div>
        <ul>
          {reports.map((r, idx) => (
            <li key={idx} className="report-item">
              <div className="report-index">{idx + 1}</div>
              <div className="report-content">
                <strong>{r.gearType} ({r.gearId})</strong>
                <div>({r.lat}, {r.lng})</div>
                <div>{r.timestamp}</div>
                <div>{calculateElapsed(r.timestamp)}</div>
              </div>
              <div className={`status-box ${r.status === '수거완료' ? 'green' : 'red'}`}></div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
};

export default Dashboard;