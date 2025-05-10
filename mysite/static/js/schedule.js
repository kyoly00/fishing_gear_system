import React, { useState, useEffect, useRef } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import { Card, CardContent } from '../components/Card';
import './Schedule.css';

const ScheduleAssignmentPage = () => {
  const calendarRef = useRef(null);

  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [vesselSchedules, setVesselSchedules] = useState([]);
  const [reportedGear, setReportedGear] = useState([]);
  const [form, setForm] = useState({
    reportId: '',
    scheduledDate: '',
    vessel: '',
    expectedLat: '',
    expectedLng: ''
  });
  const [message, setMessage] = useState('');

  // ▶ 전체 수거선 리스트
  const [vessels] = useState([
    '(유)유성환경', '(주)청해이엔티', '여순환경', '(유)덕산기업', '(유)여천위생공사',
    '(유)중앙환경건설', '(유)중앙환경건설', '(유)시민환경', '(유)동부환경', '정일환경',
    '(주)태승', '(주)그린환경', '(유)동부환경', '(유)대한환경', '(주)녹색환경산업',
    '(유)조은환경', '(유)금강환경', '자유환경산업', '(주)녹색환경산업', '(주)안전환경',
    '신성환경', '(유)시민환경', '국제환경', '보광환경', '(주)바이오테크',
    '(주)미래환경', '지구환경㈜', '지구환경㈜', '(유)구항환경', '양지환경',
    '(주)대신환경', '(주)제이에스통운', '(유)대한환경', '도시환경산업', '(유)홍주특수',
    '여수시도시관리공단', '(유)진남위생공사', '자유환경산업', '(주)유토피아', '(주)청해이엔티',
    '디딤터', '(주)삼광건설', '(주)미래환경', '전남환경', '(유)동부자원환경',
    '유진로지스(주)', '성산환경(주)', '성산환경㈜', '(주)부호물류', '(유)내추럴환경',
    '가나환경', '엘로맥스(주)', '양지환경', '(주)성안비철', '경호환경',
    '(유)태연물류', '창조환경', '해성환경산업', '(유)조은골재', '우주환경',
    '(유)통합환경', '(주)대신환경', '위드환경산업', '여수의료위생공사', '(유)에스티',
    '(유)대한민국만세복합물류', '빛그린환경', '동광환경', '(주)보성', '선경환경',
    '씨앤에스(주)', '해나환경', '비알에스 주식회사', '한일환경', '해성환경산업',
    '리얼환경산업', '(주)그린환경건설', '(유)여일보건위생공사', '(유)유성환경', '(유)구항환경',
    '㈜일주환경', '㈜녹색환경산업', '(유)삼려환경', '한일환경', '(유)우리환경',
    '(유)시민환경', '㈜주연산업', '(유)금마환경', '성산환경㈜', '(유)대한환경',
    '(유)여수환경', '신성환경', '부영환경', '(주)미래환경', '자유환경산업',
    '해양환경', '(유)중앙환경건설', '가나환경', '해성환경산업', '동성환경',
    '두성해운(주)', '위드환경산업', '우주환경', '자연환경산업', '하늘환경',
    '화양환경', '(유)통합환경', '소라환경', '양지환경', '일호산업㈜',
    '일호산업㈜', '선경환경', '구항환경산업', '덕양환경', '전남환경',
    '여천환경', '(유)로드종합건설', '㈜바른환경', '동성E&I', '동백환경',
    '리얼환경산업', '(주)와이에스환경', '푸른환경', '(유)남해산업개발', '유연환경',
    '㈜태승', '칠성재활용㈜', '시에스코', '다빈치(주)', '다빈치(주)',
    '(유)순수리싸이클링', '정원산업㈜', '㈜대웅', '㈜삼우산업', '광일기업㈜',
    '해성자원', '원스틸자원', '㈜녹색환경산업', '양지환경', '(유)삼려환경',
    '성산환경(주)', '㈜그린환경건설'
  ]);

  // 1) 초기 로딩: 신고 리스트 세팅 + 폼 기본 날짜(1일)
  useEffect(() => {
    const today = new Date();
    setCurrentYear(today.getFullYear());
    setCurrentMonth(today.getMonth() + 1);

    setReportedGear([
      { id: 3, buyerId: 200055, time: '2025-02-05 01:41', lat: '34.265000', lng: '126.331000' },
      { id: 5, buyerId: 200066, time: '2025-03-19 08:24', lat: '33.819549', lng: '128.254344' },
      { id: 6, buyerId: 200069, time: '2025-03-03 10:36', lat: '33.918416', lng: '127.504751' },
    ]);

    setForm(f => ({
      ...f,
      scheduledDate: `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-01`
    }));
  }, []);

  useEffect(() => {
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
    const events = [];
  
    const toKSTDateString = (date) => {
      const kst = new Date(date.getTime() + 9 * 60 * 60 * 1000);
      return kst.toISOString().split('T')[0];
    };
  
    for (let d = 1; d <= daysInMonth; d++) {
      const dateObj = new Date(currentYear, currentMonth - 1, d);
      const dow = dateObj.getDay();
  
      if (dow >= 1 && dow <= 5) {  // 월(1) ~ 금(5)
        const count = Math.floor(Math.random() * 4) + 7;
        const shuffled = [...vessels].sort(() => Math.random() - 0.5);
        const selected = shuffled.slice(0, count);
        const dateStr = toKSTDateString(dateObj);  
        selected.forEach(v => events.push({ title: v, date: dateStr }));
      }
    }
  
    setVesselSchedules(events);
  
    calendarRef.current?.getApi().gotoDate(
      `${currentYear}-${String(currentMonth).padStart(2, '0')}-01`
    );
    setForm(f => ({
      ...f,
      scheduledDate: `${currentYear}-${String(currentMonth).padStart(2, '0')}-01`
  }));
  }, [currentYear, currentMonth, vessels]);
  

  // 폼 핸들러 & 제출
  const handleFormChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };
  const handleSubmit = e => {
    e.preventDefault();
    setMessage(`${form.reportId}번 신고가 "${form.vessel}"에 배정되었습니다.`);
  };

  const yearOptions = Array.from(
    { length: 5 },
    (_, i) => new Date().getFullYear() - 2 + i
  );
  const monthOptions = Array.from({ length: 12 }, (_, i) => i + 1);

  return (
    <div className="schedule-page">
      <div className="schedule-panel left-panel">
        <h2 className="schedule-title">수거선 배정</h2>
        <div className="calendar-wrapper">
          <div className="calendar-grid-title">
            {currentYear}년 {currentMonth}월
          </div>
          <div className="calendar-controls">
            <select value={currentYear} onChange={e => setCurrentYear(+e.target.value)}>
              {yearOptions.map(y => <option key={y} value={y}>{y}년</option>)}
            </select>
            <select value={currentMonth} onChange={e => setCurrentMonth(+e.target.value)}>
              {monthOptions.map(m => <option key={m} value={m}>{m}월</option>)}
            </select>
          </div>
          <FullCalendar
            plugins={[dayGridPlugin]}
            initialView="dayGridMonth"
            locale="ko"
            headerToolbar={{ left: '', center: '', right: '' }}
            firstDay={1} 
            events={vesselSchedules}
            contentHeight="auto"
            ref={calendarRef}
            height={800}
            eventDisplay="list-item"
            dayMaxEventRows={false}
            dayCellClassNames={() => []}
          />
        </div>
      </div>

      <div className="schedule-panel right-panel">
        <h2 className="schedule-header">수거 예정 리스트</h2>
        {reportedGear.map(r => (
          <Card key={r.id} className="gear-card">
            <CardContent>
              <p><strong>신고 번호:</strong> {r.id}</p>
              <p><strong>구매자 ID:</strong> {r.buyerId}</p>
              <p><strong>신고 일자:</strong> {r.time}</p>
              <p><strong>위치(위도):</strong> {r.lat}</p>
              <p><strong>위치(경도):</strong> {r.lng}</p>
            </CardContent>
          </Card>
        ))}

        <div className="assignment-form">
          <h2 className="schedule-header">수거선 배정 폼</h2>
          <form onSubmit={handleSubmit}>
            <label>
              신고 번호:
              <select name="reportId" value={form.reportId} onChange={handleFormChange} required>
                <option value="" disabled>선택...</option>
                {reportedGear.map(r => <option key={r.id} value={r.id}>{r.id}</option>)}
              </select>
            </label>

            <label>
              수거 예정 날짜:
              <select name="scheduledDate" value={form.scheduledDate} onChange={handleFormChange} required>
                {Array.from(
                  { length: new Date(currentYear, currentMonth, 0).getDate() },
                  (_, i) => {
                    const d = `${currentYear}-${String(currentMonth).padStart(2,'0')}-${String(i+1).padStart(2,'0')}`;
                    return <option key={d} value={d}>{d}</option>;
                  }
                )}
              </select>
            </label>

            <label>
              수거선:
              <select name="vessel" value={form.vessel} onChange={handleFormChange} required>
                <option value="" disabled>선택...</option>
                {vessels.map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            </label>

            <label>
              예상 위치(위도):
              <input
                name="expectedLat"
                type="number"
                step="0.000001"
                value={form.expectedLat}
                onChange={handleFormChange}
                required
              />
            </label>

            <label>
              예상 위치(경도):
              <input
                name="expectedLng"
                type="number"
                step="0.000001"
                value={form.expectedLng}
                onChange={handleFormChange}
                required
              />
            </label>

            <button type="submit">배정하기</button>
          </form>
          {message && <p className="assignment-message">{message}</p>}
        </div>
      </div>
    </div>
  );
};

export default ScheduleAssignmentPage;