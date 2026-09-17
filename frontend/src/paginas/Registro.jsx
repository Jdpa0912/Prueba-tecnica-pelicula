import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../servicios/api'

export default function Registro() {
  const [formulario, setFormulario] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')
  const [cargando, setCargando] = useState(false)
  const navegar = useNavigate()

  const enviar = async (evento) => {
    evento.preventDefault()
    setError('')
    setExito('')
    setCargando(true)
    try {
      await api.post('/auth/register', formulario)
      setExito('Cuenta creada correctamente. Redirigiendo al inicio de sesión…')
      window.setTimeout(() => navegar('/login'), 1000)
    } catch (respuestaError) {
      setError(respuestaError.response?.data?.detail || 'No fue posible crear la cuenta.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <main className="pagina-auth">
      <form className="tarjeta-auth" onSubmit={enviar}>
        <p className="eyebrow">CineFavoritos</p>
        <h1>Crea tu cuenta</h1>
        <label>Usuario<input required minLength="3" value={formulario.username} onChange={(e) => setFormulario({ ...formulario, username: e.target.value })} /></label>
        <label>Contraseña<input required type="password" minLength="8" value={formulario.password} onChange={(e) => setFormulario({ ...formulario, password: e.target.value })} /></label>
        {error && <p className="mensaje error" role="alert">{error}</p>}
        {exito && <p className="mensaje exito" role="status">{exito}</p>}
        <button className="boton" disabled={cargando}>{cargando ? 'Creando…' : 'Crear cuenta'}</button>
        <p>¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link></p>
      </form>
    </main>
  )
}
