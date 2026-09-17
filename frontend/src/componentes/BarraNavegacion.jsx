import { NavLink, useNavigate } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'

export default function BarraNavegacion() {
  const { cerrarSesion } = useAutenticacion()
  const navegar = useNavigate()

  const salir = () => {
    cerrarSesion()
    navegar('/login')
  }

  return (
    <header className="barra-navegacion">
      <NavLink className="marca" to="/buscar">CineFavoritos</NavLink>
      <nav aria-label="Navegación principal">
        <NavLink to="/buscar">Buscar</NavLink>
        <NavLink to="/favoritos">Mis favoritos</NavLink>
        <button type="button" className="boton enlace-boton" onClick={salir}>Cerrar sesión</button>
      </nav>
    </header>
  )
}
