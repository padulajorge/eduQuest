import { Link, useLocation } from 'react-router-dom'
import './Header.css'

const Header = () => {
  const location = useLocation()

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          <img src="/Logo.svg" alt="EduQuest Logo" className="logo-image" onError={(e) => { e.target.style.display = 'none' }} />
          <span className="logo-text">EduQuest</span>
        </Link>
        
        <nav className="header-nav">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            <i className="fas fa-home"></i>
            <span>Inicio</span>
          </Link>
          <Link 
            to="/about-us" 
            className={`nav-link ${location.pathname === '/about-us' ? 'active' : ''}`}
          >
            <i className="fas fa-users"></i>
            <span>Sobre Nosotros</span>
          </Link>
        </nav>
      </div>
    </header>
  )
}

export default Header

