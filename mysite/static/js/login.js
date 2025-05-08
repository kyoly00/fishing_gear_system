import { useNavigate } from 'react-router-dom';
import React, { useState } from 'react';
import './Login.css'; 
import logoImg from './logo.jpg'; 

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // 로그인 로직 (예: API 인증 등) 가능
    navigate('/dashboard'); 
  };
  const handleRegister = () => {
    navigate('/register'); // 회원가입 페이지로 이동
  };


	return (
		<div className="login-vertical-wrapper">
			<div className="login-box">
				{/* 로고와 텍스트 수평 정렬 */}
				<div className="login-logo-row">
					<img src={logoImg} alt="로고" className="login-logo-img" />
				</div>

				<form onSubmit={handleSubmit} className="login-form">
					<label>ID</label>
					<input
						type="text"
						value={username}
						onChange={(e) => setUsername(e.target.value)}
						required
					/>
					<label>PW</label>
					<input
						type="password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						required
					/>
					<div className="login-button-wrapper">
						<button type="submit" className="login-button">로그인</button>
						<button type="button" className="register-button" onClick={handleRegister}>
						회원가입
						</button>
					</div>
        </form>
      </div>
     </div>
  );
};

export default Login;
