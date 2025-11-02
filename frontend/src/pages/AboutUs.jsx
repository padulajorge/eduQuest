import Header from '../components/Header'
import './AboutUs.css'

const AboutUs = () => {
  return (
    <div className="about-us-page">
      
      <main className="about-us-content">
      <Header />
        <section className="hero-section">
          <h1 className="hero-title animate-fade-in-up">Sobre Nosotros</h1>
          <p className="hero-subtitle animate-fade-in-up">
            Trabajo colaborativo integrador - Seminario de Actualización Tecnológica I
          </p>
        </section>

        <section className="about-section">
          <div className="content-card animate-fade-in-up">
            <h2>El Proyecto</h2>
            <p>
              <strong>EduQuest</strong> es el resultado de un trabajo colaborativo e integrador 
              desarrollado para la cátedra de <strong>Seminario de Actualización Tecnológica I</strong>. 
              Aplicando los conocimientos técnicos adquiridos durante el curso de nuestras carreras, 
              en conjunto con la experta guía del equipo de cátedra y alumnos avanzados, desarrollamos 
              esta aplicación que hace uso de tecnologías innovadoras y actuales.
            </p>
            <p>
              Nuestro objetivo es ampliar el repertorio de nuestros docentes y compañeros alumnos 
              a la hora de estudiar o diseñar una evaluación, facilitando la creación de materiales 
              educativos de calidad mediante el uso de inteligencia artificial.
            </p>
          </div>

          <div className="content-card animate-fade-in-up">
            <h2>¿Qué Hacemos?</h2>
            <p>
              EduQuest es una plataforma innovadora que utiliza inteligencia artificial para 
              analizar textos y generar automáticamente preguntas de comprensión lectora. 
              Ya sea un artículo, un documento académico o cualquier texto, nuestra IA 
              identifica conceptos clave y crea preguntas adaptadas al nivel de dificultad 
              que elijas.
            </p>
          </div>

          <div className="content-card animate-fade-in-up">
            <h2>Nuestro Equipo</h2>
            <div className="team-grid">
              <div className="team-member">
                <div className="member-icon">
                  <i className="fas fa-user-graduate"></i>
                </div>
                <h4>Padula Lugo Jorge Enrique Martin</h4>
                <p>Alumno de 3er año de Ingeniería en Sistemas de Información</p>
              </div>
              <div className="team-member">
                <div className="member-icon">
                  <i className="fas fa-user-graduate"></i>
                </div>
                <h4>Artico Francisco</h4>
                <p>Alumno de 3er año de Ingeniería en Sistemas de Información</p>
              </div>
              <div className="team-member">
                <div className="member-icon">
                  <i className="fas fa-user-graduate"></i>
                </div>
                <h4>Arias Simone Mariano</h4>
                <p>Alumno de 3er año de Ingeniería en Sistemas de Información</p>
              </div>
              <div className="team-member">
                <div className="member-icon">
                  <i className="fas fa-user-graduate"></i>
                </div>
                <h4>Ulices Victor Hugo Barros Muñoz</h4>
                <p>Alumno de 3er año de Ingeniería en Sistemas de Información</p>
              </div>
              <div className="team-member">
                <div className="member-icon">
                  <i className="fas fa-user-graduate"></i>
                </div>
                <h4>Alejandro</h4>
                <p>Alumno de 5to año de Ingeniería en Sistemas de Información</p>
              </div>
              <div className="team-member">
                <div className="member-icon">
                  <i className="fas fa-user-graduate"></i>
                </div>
                <h4>Romero Agustín</h4>
                <p>Alumno de Licenciatura en Diseño y Producción Multimedial</p>
              </div>
            </div>
          </div>

          <div className="features-grid">
            <div className="feature-item animate-fade-in-up">
              <div className="feature-icon">
                <i className="fas fa-brain"></i>
              </div>
              <h3>IA Avanzada</h3>
              <p>
                Utilizamos modelos de lenguaje de última generación para garantizar 
                preguntas de alta calidad y precisión.
              </p>
            </div>

            <div className="feature-item animate-fade-in-up">
              <div className="feature-icon">
                <i className="fas fa-book-reader"></i>
              </div>
              <h3>Para Todos</h3>
              <p>
                Ideal para estudiantes que quieren practicar, profesores que necesitan 
                crear materiales didácticos y profesionales de la educación.
              </p>
            </div>

            <div className="feature-item animate-fade-in-up">
              <div className="feature-icon">
                <i className="fas fa-cogs"></i>
              </div>
              <h3>Personalizable</h3>
              <p>
                Ajusta la dificultad, cantidad de preguntas y tipo según tus necesidades. 
                Soporta múltiples formatos de archivo.
              </p>
            </div>

            <div className="feature-item animate-fade-in-up">
              <div className="feature-icon">
                <i className="fas fa-bolt"></i>
              </div>
              <h3>Rápido y Eficiente</h3>
              <p>
                Genera preguntas en segundos. Ahorra tiempo y enfócate en lo que realmente 
                importa: aprender y enseñar.
              </p>
            </div>
          </div>

          <div className="content-card animate-fade-in-up">
            <h2>Nuestros Valores</h2>
            <div className="values-list">
              <div className="value-item">
                <i className="fas fa-users"></i>
                <div>
                  <h4>Trabajo Colaborativo</h4>
                  <p>Creemos en el poder del trabajo en equipo y la colaboración interdisciplinaria para crear soluciones innovadoras.</p>
                </div>
              </div>
              <div className="value-item">
                <i className="fas fa-lightbulb"></i>
                <div>
                  <h4>Innovación Tecnológica</h4>
                  <p>Utilizamos tecnologías de vanguardia para transformar la manera en que aprendemos y enseñamos.</p>
                </div>
              </div>
              <div className="value-item">
                <i className="fas fa-graduation-cap"></i>
                <div>
                  <h4>Compromiso Educativo</h4>
                  <p>Nuestro objetivo es apoyar tanto a docentes como a estudiantes en el proceso educativo, facilitando la creación y evaluación de contenido.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default AboutUs

