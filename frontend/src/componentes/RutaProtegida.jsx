import { Navigate, useLocation } from 'react-router-dom'
import { useAutenticacion } from '../contexto/ContextoAutenticacion'

export default function RutaProtegida({ children }) {
  const { autenticado } = useAutenticacion()
  const ubicacion = useLocation()

  if (!autenticado) return <Navigate to="/login" replace state={{ desde: ubicacion }} />
  return children
}
