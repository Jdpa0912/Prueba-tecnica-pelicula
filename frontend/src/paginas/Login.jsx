import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'
import api from '../servicios/api'

export default function Login() {
  const [formulario, setFormulario] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)
  const { iniciarSesion } = useAutenticacion()
  const navegar = useNavigate()
  const ubicacion = useLocation()

  const enviar = async (evento) => {
    evento.preventDefault()
    setError('')
    setCargando(true)
    try {
      const { data } = await api.post('/auth/login', formulario)
      iniciarSesion(data.access_token)
      navegar(ubicacion.state?.desde?.pathname || '/buscar', { replace: true })
    } catch (respuestaError) {
      setError(respuestaError.response?.data?.detail || 'No fue posible iniciar sesión.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <main className="pagina-auth">
      <form className="tarjeta-auth" onSubmit={enviar}>
        <p className="eyebrow">CineFavoritos</p>
        <h1>Inicia sesión</h1>
        <label>Usuario<input required value={formulario.username} onChange={(e) => setFormulario({ ...formulario, username: e.target.value })} /></label>
        <label>Contraseña<input required type="password" value={formulario.password} onChange={(e) => setFormulario({ ...formulario, password: e.target.value })} /></label>
        {error && <p className="mensaje error" role="alert">{error}</p>}
        <button className="boton" disabled={cargando}>{cargando ? 'Ingresando…' : 'Ingresar'}</button>
        <p>¿No tienes cuenta? <Link to="/registro">Regístrate</Link></p>
      </form>
    </main>
  )
}
