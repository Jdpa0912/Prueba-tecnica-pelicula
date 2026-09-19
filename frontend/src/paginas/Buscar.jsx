import { useState } from 'react'
import TarjetaPelicula from '../componentes/TarjetaPelicula'
import api from '../servicios/api'

export default function Buscar() {
  const [termino, setTermino] = useState('')
  const [peliculas, setPeliculas] = useState([])
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')
  const [peliculasFavoritas, setPeliculasFavoritas] = useState(() => new Set())
  const [peliculasAgregando, setPeliculasAgregando] = useState(() => new Set())

  const buscar = async (evento) => {
    evento.preventDefault()
    const consulta = termino.trim()
    if (!consulta) return
    setCargando(true); setError(''); setMensaje('')
    try {
      const { data } = await api.get('/peliculas/buscar', { params: { q: consulta } })
      setPeliculas(data)
      if (data.length === 0) setMensaje('No encontramos películas para esta búsqueda.')
    } catch (respuestaError) {
      setError(respuestaError.response?.data?.detail || 'No se pudo completar la búsqueda.')
    } finally { setCargando(false) }
  }

  const agregarFavorito = async (pelicula) => {
    if (peliculasFavoritas.has(pelicula.pelicula_id) || peliculasAgregando.has(pelicula.pelicula_id)) return

    setError(''); setMensaje('')
    setPeliculasAgregando((actuales) => new Set(actuales).add(pelicula.pelicula_id))
    try {
      await api.post('/favoritos', pelicula)
      setPeliculasFavoritas((actuales) => new Set(actuales).add(pelicula.pelicula_id))
      setMensaje(`“${pelicula.titulo}” fue agregada a favoritos.`)
    } catch (respuestaError) {
      setError(respuestaError.response?.data?.detail || 'No fue posible agregar el favorito.')
    } finally {
      setPeliculasAgregando((actuales) => {
        const siguientes = new Set(actuales)
        siguientes.delete(pelicula.pelicula_id)
        return siguientes
      })
    }
  }

  return (
    <main className="contenedor pagina">
      <section className="encabezado-pagina">
        <p className="eyebrow">Explora películas</p><h1>Encuentra tu próxima favorita</h1>
        <form className="formulario-busqueda" onSubmit={buscar}>
          <input aria-label="Buscar películas" placeholder="Ej.: El Padrino" value={termino} onChange={(e) => setTermino(e.target.value)} />
          <button className="boton" disabled={cargando}>{cargando ? 'Buscando…' : 'Buscar'}</button>
        </form>
      </section>
      {error && <p className="mensaje error" role="alert">{error}</p>}
      {mensaje && <p className="mensaje exito" role="status">{mensaje}</p>}
      {cargando ? <div className="cargando" role="status">Buscando películas…</div> : (
        <section className="rejilla-peliculas" aria-live="polite">
          {peliculas.map((pelicula) => {
            const yaEsFavorita = peliculasFavoritas.has(pelicula.pelicula_id)
            const agregando = peliculasAgregando.has(pelicula.pelicula_id)
            return <TarjetaPelicula key={pelicula.pelicula_id} pelicula={pelicula}><button className="boton" disabled={yaEsFavorita || agregando} onClick={() => agregarFavorito(pelicula)}>{yaEsFavorita ? 'En favoritos' : agregando ? 'Agregando…' : 'Agregar a favoritos'}</button></TarjetaPelicula>
          })}
        </section>
      )}
    </main>
  )
}
