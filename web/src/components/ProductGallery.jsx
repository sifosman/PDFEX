import PropTypes from 'prop-types'

export default function ProductGallery({ product }) {
  const images = product.image_urls && product.image_urls.length > 0 ? product.image_urls : []
  if (images.length <= 1) return null

  return (
    <div className="thumbnail-strip">
      {images.slice(1).map((url, index) => (
        <img key={url} src={url} alt={`${product.displayName} alt ${index + 1}`} loading="lazy" />
      ))}
    </div>
  )
}

ProductGallery.propTypes = {
  product: PropTypes.object.isRequired,
}
