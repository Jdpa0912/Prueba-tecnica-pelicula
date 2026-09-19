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
  const [ordenarPor, setOrdenarPor] = useState('fecha')
  const [direccion, setDireccion] = useState('desc')

  const cargarFavoritos = async (orden = ordenarPor, sentido = direccion) => {
    setCargando(true); setError('')
    try { const { data } = await api.get('/favoritos', { params: { ordenar_por: orden, direccion: sentido } }); setFavoritos(data) }
    catch (respuestaError) { setError(respuestaError.response?.data?.detail || 'No fue posible cargar tus favoritos.') }
    finally { setCargando(false) }
  }
  // La carga inicial debe ejecutarse una sola vez; los cambios de orden se manejan en cambiarOrden.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { cargarFavoritos() }, [])

  const cambiarOrden = (evento) => {
    const [orden, sentido] = evento.target.value.split(':')
    setOrdenarPor(orden); setDireccion(sentido)
    cargarFavoritos(orden, sentido)
  }

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
        <>
          <div className="controles-favoritos">
            <label htmlFor="orden-favoritos">Ordenar favoritas</label>
            <select id="orden-favoritos" value={`${ordenarPor}:${direccion}`} onChange={cambiarOrden}>
              <option value="fecha:desc">Más recientes</option>
              <option value="year:desc">Año: más reciente</option>
              <option value="year:asc">Año: más antiguo</option>
              <option value="estrellas:desc">Estrellas: mayor calificación</option>
              <option value="estrellas:asc">Estrellas: menor calificación</option>
            </select>
          </div>
        <section className="rejilla-peliculas">
          {favoritos.map((favorito) => <TarjetaPelicula key={favorito.id} pelicula={favorito}>
            <p className="calificacion-guardada" aria-label={`Calificación: ${favorito.estrellas} de 5 estrellas`}>{'★'.repeat(favorito.estrellas)}{'☆'.repeat(5 - favorito.estrellas)} <span>{favorito.estrellas}/5</span></p>
            {editando === favorito.id ? <div className="edicion-nota"><textarea value={nota} onChange={(e) => setNota(e.target.value)} placeholder="Tu nota personal" /><button className="boton" onClick={() => guardarNota(favorito.id)}>Guardar nota</button><button className="boton secundario" onClick={() => setEditando(null)}>Cancelar</button></div> : <><p className="nota">{favorito.nota || 'Sin nota personal.'}</p><div className="acciones"><button className="boton secundario" onClick={() => { setEditando(favorito.id); setNota(favorito.nota || '') }}>Editar nota</button><button className="boton peligro" onClick={() => eliminar(favorito.id)}>Eliminar</button></div></>}
          </TarjetaPelicula>)}
        </section>
        </>
      )}
    </main>
  )
}
