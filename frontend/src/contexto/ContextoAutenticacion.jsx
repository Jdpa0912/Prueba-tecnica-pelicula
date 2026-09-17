/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useMemo, useState } from 'react'

const ContextoAutenticacion = createContext(null)

export function ProveedorAutenticacion({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  const iniciarSesion = (nuevoToken) => {
    localStorage.setItem('token', nuevoToken)
    setToken(nuevoToken)
  }

  const cerrarSesion = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  const valor = useMemo(
    () => ({ token, autenticado: Boolean(token), iniciarSesion, cerrarSesion }),
    [token],
  )

  return <ContextoAutenticacion.Provider value={valor}>{children}</ContextoAutenticacion.Provider>
}

export function useAutenticacion() {
  const contexto = useContext(ContextoAutenticacion)
  if (!contexto) throw new Error('useAutenticacion debe usarse dentro de ProveedorAutenticacion.')
  return contexto
}
