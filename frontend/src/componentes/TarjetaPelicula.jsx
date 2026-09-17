const POSTER_PLACEHOLDER = 'https://placehold.co/600x900/1f2937/ffffff?text=Sin+p%C3%B3ster'

export default function TarjetaPelicula({ pelicula, children }) {
  const manejarErrorPoster = (evento) => {
    evento.currentTarget.onerror = null
    evento.currentTarget.src = POSTER_PLACEHOLDER
  }

  return (
    <article className="tarjeta-pelicula">
      <img
        src={pelicula.poster || POSTER_PLACEHOLDER}
        alt={pelicula.titulo ? `Póster de ${pelicula.titulo}` : 'Póster no disponible'}
        onError={manejarErrorPoster}
      />
      <div className="contenido-tarjeta">
        <h2>{pelicula.titulo}</h2>
        <p>{pelicula.year || 'Año no disponible'}</p>
        {children}
      </div>
    </article>
  )
}
