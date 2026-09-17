import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import BarraNavegacion from './componentes/BarraNavegacion'
import RutaProtegida from './componentes/RutaProtegida'
import { ProveedorAutenticacion } from './contexto/ContextoAutenticacion'
import Buscar from './paginas/Buscar'
import Favoritos from './paginas/Favoritos'
import Login from './paginas/Login'
import Registro from './paginas/Registro'
import './App.css'

function PantallaProtegida({ children }) { return <><BarraNavegacion />{children}</> }

export default function App() {
  return <ProveedorAutenticacion><BrowserRouter><Routes>
    <Route path="/login" element={<Login />} /><Route path="/registro" element={<Registro />} />
    <Route path="/buscar" element={<RutaProtegida><PantallaProtegida><Buscar /></PantallaProtegida></RutaProtegida>} />
    <Route path="/favoritos" element={<RutaProtegida><PantallaProtegida><Favoritos /></PantallaProtegida></RutaProtegida>} />
    <Route path="*" element={<Navigate to="/buscar" replace />} />
  </Routes></BrowserRouter></ProveedorAutenticacion>
}
