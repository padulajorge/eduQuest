import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [texto, setTexto] = useState('')
  const [archivo, setArchivo] = useState(null)
  const [tipo, setTipo] = useState('multiple_choice')
  const [cantidadPreguntas, setCantidadPreguntas] = useState(5)
  const [opcionesPorPregunta, setOpcionesPorPregunta] = useState(4)
  const [nivelDificultad, setNivelDificultad] = useState('intermedio')
  const [preguntas, setPreguntas] = useState([])
  const [respuestas, setRespuestas] = useState({})
  const [mostrarPreguntas, setMostrarPreguntas] = useState(false)
  const [cargando, setCargando] = useState(false)
  const [resultados, setResultados] = useState({})
  const [preguntasVerificadas, setPreguntasVerificadas] = useState({})
  const [currentCardIndex, setCurrentCardIndex] = useState(0)

  // Carrusel automático para las tarjetas de características en móviles
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentCardIndex((prevIndex) => (prevIndex + 1) % 3)
    }, 3000) // Cambia cada 3 segundos

    return () => clearInterval(interval)
  }, [])

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setArchivo(file)
      setTexto('') // Limpiar texto si se sube archivo
    }
  }


  const generarPreguntas = async () => {
    if (!texto && !archivo) {
      alert('Por favor ingresa texto o sube un archivo')
      return
    }

    setCargando(true)
    
    try {
      const formData = new FormData()
      
      if (archivo) {
        formData.append('file', archivo)
      } else {
        formData.append('contexto', texto)
      }
      
      formData.append('tipo', tipo)
      formData.append('cantidad_preguntas', cantidadPreguntas.toString())
      formData.append('opciones_por_pregunta', opcionesPorPregunta.toString())
      formData.append('nivel_dificultad', nivelDificultad)
      formData.append('modelo', 'gpt-4o')
      formData.append('force_ocr', 'false')
      formData.append('ocr_lang', 'spa+eng')

      const response = await fetch('http://localhost:8000/chat/generar-preguntas', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        // Intentar obtener el mensaje de error del backend
        let errorMessage = `Error ${response.status}`
        try {
          const errorData = await response.json()
          if (errorData.detail) {
            errorMessage = errorData.detail
          }
        } catch (e) {
          // Si no se puede parsear el JSON, usar el mensaje por defecto
          errorMessage = `Error ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setPreguntas(data.preguntas || [])
      setMostrarPreguntas(true)
      setRespuestas({})
      setResultados({})
      setPreguntasVerificadas({})
    } catch (error) {
      console.error('Error:', error)
      alert('Error al generar preguntas: ' + error.message)
    } finally {
      setCargando(false)
    }
  }

  const handleRespuesta = (preguntaId, respuesta) => {
    setRespuestas(prev => ({
      ...prev,
      [preguntaId]: respuesta
    }))
  }

  const verificarRespuestaIndividual = (preguntaIndex) => {
    const pregunta = preguntas[preguntaIndex]
    const respuestaUsuario = respuestas[preguntaIndex]
    
    if (!respuestaUsuario) {
      alert('Por favor selecciona una respuesta antes de verificar')
      return
    }

    const esCorrecta = respuestaUsuario === pregunta.respuesta_correcta
    
    setPreguntasVerificadas(prev => ({
      ...prev,
      [preguntaIndex]: {
        esCorrecta,
        respuestaCorrecta: pregunta.respuesta_correcta,
        respuestaUsuario
      }
    }))
  }

  const reiniciarCuestionario = () => {
    setRespuestas({})
    setResultados({})
    setPreguntasVerificadas({})
  }

  const reiniciar = () => {
    setPreguntas([])
    setRespuestas({})
    setResultados({})
    setPreguntasVerificadas({})
    setMostrarPreguntas(false)
    setTexto('')
    setArchivo(null)
  }

  // Datos de las tarjetas de características
  const featureCards = [
    {
      icon: "fas fa-brain",
      title: "Análisis Inteligente",
      description: "La IA analiza el contenido e identifica conceptos clave automáticamente"
    },
    {
      icon: "fas fa-sparkles",
      title: "Preguntas Variadas",
      description: "Genera preguntas de opción múltiple y verdadero/falso adaptadas al texto"
    },
    {
      icon: "fas fa-book-open",
      title: "Feedback Inmediato",
      description: "Recibe retroalimentación instantánea sobre tus respuestas"
    }
  ]

  return (
    <div className="app">
      {/* Header */}
      <div className="header-section animate-fade-in">
        <div className="badge animate-slide-down">
          <i className="fas fa-sparkles"></i>
          Revolucionando la Comprensión Lectora con IA
        </div>
        <h1 className="animate-slide-up">Genera Preguntas de Comprensión Lectora</h1>
        <p className="animate-fade-in-delay">Ingresa cualquier texto y nuestra IA creará preguntas personalizadas para verificar la comprensión. Perfecto para estudiantes y profesores.</p>
      </div>

      {/* Feature Cards */}
      <div className="feature-cards">
        {/* Desktop: Mostrar todas las tarjetas */}
        <div className="feature-cards-desktop">
          {featureCards.map((card, index) => (
            <div key={index} className="feature-card animate-slide-up" style={{animationDelay: `${(index + 1) * 0.1}s`}}>
              <i className={card.icon}></i>
              <h3>{card.title}</h3>
              <p>{card.description}</p>
            </div>
          ))}
        </div>
        
        {/* Mobile: Carrusel con una tarjeta a la vez */}
        <div className="feature-cards-mobile">
          <div className="carousel-container">
            <div className="feature-card carousel-card animate-fade-in">
              <i className={featureCards[currentCardIndex].icon}></i>
              <h3>{featureCards[currentCardIndex].title}</h3>
              <p>{featureCards[currentCardIndex].description}</p>
            </div>
          </div>
        </div>
      </div>

      {!mostrarPreguntas ? (
        /* Input Section */
        <div className="input-section animate-fade-in">
          <h2 className="animate-slide-up">Ingresa tu Texto</h2>
          <p className="animate-fade-in-delay">Escribe texto o sube un archivo (TXT, PDF, DOC, DOCX) para generar preguntas de comprensión</p>

          {/* File Upload */}
          <div className="file-upload">
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileChange}
              className="d-none"
            />
            <label htmlFor="file-upload" className="btn btn-outline-secondary">
              <i className="fas fa-upload"></i> Subir Archivo (TXT, PDF, DOC, DOCX)
            </label>
            {archivo && <span className="file-name">{archivo.name}</span>}
          </div>

          {/* Text Input */}
          <textarea
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Ejemplo: La fotosíntesis es el proceso mediante el cual las plantas convierten la luz solar en energía química..."
            className="form-control"
            rows="6"
            disabled={!!archivo}
          />

          {/* Configuration */}
          <div className="config-section animate-slide-up" style={{animationDelay: '0.2s'}}>
            <div className="config-group">
              <label>Tipo de Preguntas:</label>
              <select 
                value={tipo} 
                onChange={(e) => setTipo(e.target.value)}
                className="form-select"
              >
                <option value="multiple_choice">Opción Múltiple</option>
                <option value="verdadero_falso">Verdadero/Falso</option>
              </select>
            </div>

            <div className="config-group">
              <label>Cantidad de Preguntas:</label>
              <select 
                value={cantidadPreguntas} 
                onChange={(e) => setCantidadPreguntas(parseInt(e.target.value))}
                className="form-select"
              >
                <option value="3">3</option>
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
              </select>
            </div>

            {tipo === 'multiple_choice' && (
              <div className="config-group">
                <label>Opciones por Pregunta:</label>
                <select 
                  value={opcionesPorPregunta} 
                  onChange={(e) => setOpcionesPorPregunta(parseInt(e.target.value))}
                  className="form-select"
                >
                  <option value="3">3</option>
                  <option value="4">4</option>
                  <option value="5">5</option>
                </select>
              </div>
            )}

            <div className="config-group">
              <label>Nivel de Dificultad:</label>
              <select 
                value={nivelDificultad} 
                onChange={(e) => setNivelDificultad(e.target.value)}
                className="form-select"
              >
                <option value="basico">Básico</option>
                <option value="intermedio">Intermedio</option>
                <option value="avanzado">Avanzado</option>
              </select>
            </div>
          </div>

          <button 
            onClick={generarPreguntas}
            className="btn btn-primary btn-generate animate-pulse"
            disabled={cargando || (!texto && !archivo)}
          >
            <i className="fas fa-paper-plane"></i> 
            {cargando ? 'Generando...' : 'Generar Preguntas'}
          </button>
        </div>
      ) : (
        /* Questions Section */
        <div className="questions-section animate-fade-in">
          <div className="questions-header animate-slide-down">
            <h2>Preguntas de Comprensión Lectora</h2>
            <div className="header-buttons">
              <button onClick={reiniciarCuestionario} className="btn btn-outline-primary animate-bounce">
                <i className="fas fa-redo"></i> Reiniciar Cuestionario
              </button>
              <button onClick={reiniciar} className="btn btn-outline-secondary animate-bounce">
                <i className="fas fa-refresh"></i> Nuevo Texto
              </button>
            </div>
          </div>

          <div className="questions-container">
            {preguntas.map((pregunta, index) => (
              <div key={index} className="question-card animate-slide-up" style={{animationDelay: `${index * 0.1}s`}}>
                <h4>Pregunta {index + 1}</h4>
                <p className="question-text">{pregunta.pregunta}</p>
                
                <div className="options">
                  {pregunta.opciones ? (
                    pregunta.opciones.map((opcion, opcionIndex) => (
                      <label key={opcionIndex} className="option-label">
                        <input
                          type="radio"
                          name={`pregunta-${index}`}
                          value={opcion}
                          onChange={() => handleRespuesta(index, opcion)}
                          checked={respuestas[index] === opcion}
                          disabled={Object.keys(resultados).length > 0}
                        />
                        <span className={`option-text ${
                          preguntasVerificadas[index] ? (
                            opcion === preguntasVerificadas[index].respuestaCorrecta ? 'correct-option' :
                            opcion === preguntasVerificadas[index].respuestaUsuario && !preguntasVerificadas[index].esCorrecta ? 'incorrect-option' : ''
                          ) : ''
                        }`}>{opcion}</span>
                        {preguntasVerificadas[index] && opcion === respuestas[index] && (
                          <span className={`result-icon ${
                            preguntasVerificadas[index].esCorrecta ? 'correct' : 'incorrect'
                          }`}>
                            {preguntasVerificadas[index].esCorrecta ? '✓' : '✗'}
                          </span>
                        )}
                      </label>
                    ))
                  ) : (
                    <div className="true-false-options">
                      <label className="option-label">
                        <input
                          type="radio"
                          name={`pregunta-${index}`}
                          value="Verdadero"
                          onChange={() => handleRespuesta(index, 'Verdadero')}
                          checked={respuestas[index] === 'Verdadero'}
                          disabled={Object.keys(resultados).length > 0}
                        />
                        <span className={`option-text ${
                          preguntasVerificadas[index] ? (
                            'Verdadero' === preguntasVerificadas[index].respuestaCorrecta ? 'correct-option' :
                            'Verdadero' === preguntasVerificadas[index].respuestaUsuario && !preguntasVerificadas[index].esCorrecta ? 'incorrect-option' : ''
                          ) : ''
                        }`}>Verdadero</span>
                        {preguntasVerificadas[index] && respuestas[index] === 'Verdadero' && (
                          <span className={`result-icon ${
                            preguntasVerificadas[index].esCorrecta ? 'correct' : 'incorrect'
                          }`}>
                            {preguntasVerificadas[index].esCorrecta ? '✓' : '✗'}
                          </span>
                        )}
                      </label>
                      <label className="option-label">
                        <input
                          type="radio"
                          name={`pregunta-${index}`}
                          value="Falso"
                          onChange={() => handleRespuesta(index, 'Falso')}
                          checked={respuestas[index] === 'Falso'}
                          disabled={Object.keys(resultados).length > 0}
                        />
                        <span className={`option-text ${
                          preguntasVerificadas[index] ? (
                            'Falso' === preguntasVerificadas[index].respuestaCorrecta ? 'correct-option' :
                            'Falso' === preguntasVerificadas[index].respuestaUsuario && !preguntasVerificadas[index].esCorrecta ? 'incorrect-option' : ''
                          ) : ''
                        }`}>Falso</span>
                        {preguntasVerificadas[index] && respuestas[index] === 'Falso' && (
                          <span className={`result-icon ${
                            preguntasVerificadas[index].esCorrecta ? 'correct' : 'incorrect'
                          }`}>
                            {preguntasVerificadas[index].esCorrecta ? '✓' : '✗'}
                          </span>
                        )}
                      </label>
                    </div>
                  )}
                </div>

                {preguntasVerificadas[index] && !preguntasVerificadas[index].esCorrecta && (
                  <div className="correct-answer">
                    <strong>Respuesta correcta:</strong> {preguntasVerificadas[index].respuestaCorrecta}
                  </div>
                )}

                {!preguntasVerificadas[index] && (
                  <div className="verify-question-section animate-fade-in">
                    <button 
                      onClick={() => verificarRespuestaIndividual(index)}
                      className="btn btn-verify-individual animate-pulse"
                      disabled={!respuestas[index]}
                    >
                      <i className="fas fa-check"></i> Verificar
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {Object.keys(preguntasVerificadas).length > 0 && (
            <div className="results-section animate-fade-in">
              <h3 className="animate-slide-up">Progreso</h3>
              <div className="score animate-bounce">
                {Object.values(preguntasVerificadas).filter(r => r.esCorrecta).length} de {preguntas.length} correctas
              </div>
              <div className="percentage animate-pulse">
                {Math.round((Object.values(preguntasVerificadas).filter(r => r.esCorrecta).length / preguntas.length) * 100)}%
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
