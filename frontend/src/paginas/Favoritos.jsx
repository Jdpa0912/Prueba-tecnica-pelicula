/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react'
import TarjetaPelicula from '../componentes/TarjetaPelicula'
import api from '../servicios/api'

export default function Favoritos() {
  const [favoritos, setFavoritos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [editando, setEditando] = useState(null)
  const [nota, setNota] = useState('')

  const cargarFavoritos = async () => {
    setCargando(true); setError('')
    try { const { data } = await api.get('/favoritos'); setFavoritos(data) }
    catch (respuestaError) { setError(respuestaError.response?.data?.detail || 'No fue posible cargar tus favoritos.') }
    finally { setCargando(false) }
  }
  useEffect(() => { cargarFavoritos() }, [])

  const eliminar = async (id) => {
    setError(''); setMensaje('')
    try { await api.delete(`/favoritos/${id}`); setFavoritos((actuales) => actuales.filter((favorito) => favorito.id !== id)); setMensaje('Favorito eliminado correctamente.') }
    catch (respuestaError) { setError(respuestaError.response?.data?.detail || 'No fue posible eliminar el favorito.') }
  }
  const guardarNota = async (id) => {
    setError(''); setMensaje('')
    try {
      const { data } = await api.put(`/favoritos/${id}`, { nota })
      setFavoritos((actuales) => actuales.map((favorito) => favorito.id === id ? data : favorito))
      setEditando(null); setMensaje('Nota actualizada correctamente.')
    } catch (respuestaError) { setError(respuestaError.response?.data?.detail || 'No fue posible actualizar la nota.') }
  }

  return (
    <main className="contenedor pagina">
      <section className="encabezado-pagina"><p className="eyebrow">Tu colección</p><h1>Mis favoritos</h1></section>
      {error && <p className="mensaje error" role="alert">{error}</p>}
      {mensaje && <p className="mensaje exito" role="status">{mensaje}</p>}
      {cargando ? <div className="cargando" role="status">Cargando favoritos…</div> : favoritos.length === 0 ? <p className="estado-vacio">Aún no tienes películas favoritas. ¡Busca una y agrégala a tu lista!</p> : (
        <section className="rejilla-peliculas">
          {favoritos.map((favorito) => <TarjetaPelicula key={favorito.id} pelicula={favorito}>
            {editando === favorito.id ? <div className="edicion-nota"><textarea value={nota} onChange={(e) => setNota(e.target.value)} placeholder="Tu nota personal" /><button className="boton" onClick={() => guardarNota(favorito.id)}>Guardar nota</button><button className="boton secundario" onClick={() => setEditando(null)}>Cancelar</button></div> : <><p className="nota">{favorito.nota || 'Sin nota personal.'}</p><div className="acciones"><button className="boton secundario" onClick={() => { setEditando(favorito.id); setNota(favorito.nota || '') }}>Editar nota</button><button className="boton peligro" onClick={() => eliminar(favorito.id)}>Eliminar</button></div></>}
          </TarjetaPelicula>)}
        </section>
      )}
    </main>
  )
}
