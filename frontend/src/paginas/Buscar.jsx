import { useState } from 'react'
import TarjetaPelicula from '../componentes/TarjetaPelicula'
import api from '../servicios/api'

export default function Buscar() {
  const [termino, setTermino] = useState('')
  const [peliculas, setPeliculas] = useState([])
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')

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
    setError(''); setMensaje('')
    try {
      await api.post('/favoritos', pelicula)
      setMensaje(`“${pelicula.titulo}” fue agregada a favoritos.`)
    } catch (respuestaError) {
      setError(respuestaError.response?.data?.detail || 'No fue posible agregar el favorito.')
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
          {peliculas.map((pelicula) => <TarjetaPelicula key={pelicula.pelicula_id} pelicula={pelicula}><button className="boton" onClick={() => agregarFavorito(pelicula)}>Agregar a favoritos</button></TarjetaPelicula>)}
        </section>
      )}
    </main>
  )
}
