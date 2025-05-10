import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import './Sidebar.css';
import { FaHome, FaBell, FaCalendarAlt, FaSignOutAlt } from 'react-icons/fa';
import logoImg from './assets/logo.png'; 

const Sidebar = () => {
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(false);

  const goToDashboard = () => {
    navigate('/dashboard');
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <div className="sidebar">
      <div className="sidebar-logo" onClick={goToDashboard}>
        <img src={logoImg} alt="로고" className="logo-img" />
        <h2>어구어구</h2>
      </div>

      <ul className="sidebar-menu">
        <li>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-active' : ''}>
            <FaHome className="icon" />
            <span>실시간 유실 어구</span>
          </NavLink>
        </li>

        <li className="menu-item">
          <div className="menu-title" onClick={toggleExpand}>
            <FaBell className="icon" />
            <span>어구 관리</span>
          </div>
          {isExpanded && (
            <ul className="sub-menu">
              <li>
                <NavLink to="/report" className={({ isActive }) => isActive ? 'nav-active' : ''}>
                  <span>신고 정보 관리</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/buyer" className={({ isActive }) => isActive ? 'nav-active' : ''}>
                  <span>구매 정보 관리</span>
                </NavLink>
              </li>
            </ul>
          )}
        </li>

        <li>
          <NavLink to="/schedule" className={({ isActive }) => isActive ? 'nav-active' : ''}>
            <FaCalendarAlt className="icon" />
            <span>수거선 배정</span>
          </NavLink>
        </li>
      </ul>

      <div className="sidebar-logout" onClick={handleLogout}>
        <FaSignOutAlt className="icon" />
        <span>로그아웃</span>
      </div>
    </div>
  );
};

export default Sidebar;