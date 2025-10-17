import PropTypes from 'prop-types'
import { clsx } from 'clsx'
import ProductGallery from './ProductGallery'

function ProductDetails({ product }) {
  const specs = Array.isArray(product.spec_features) ? product.spec_features : []
  const dimensions = product.dimensions || {}

  return (
    <div className="product-details">
      <div className="code">{product.product_code}</div>
      {specs.length > 0 && (
        <ul className="spec-list">
          {specs.map((spec) => (
            <li key={spec}>{spec}</li>
          ))}
        </ul>
      )}
      {Object.keys(dimensions).length > 0 && (
        <div className="dimensions">
          {Object.entries(dimensions).map(([key, value]) => (
            <div key={key}>
              <span className="label">{key}</span>
              <span className="value">
                {value.value}
                {value.unit}
              </span>
            </div>
          ))}
        </div>
      )}
      {product.pack_quantity && (
        <div className="pack-quantity">Pack of {product.pack_quantity}</div>
      )}
    </div>
  )
}

ProductDetails.propTypes = {
  product: PropTypes.object.isRequired,
}

export default function ProductCard({ product }) {
  const primaryImage = product.primary_image_url || product.image_urls[0]

  return (
    <article className="product-card">
      <div className={clsx('image-wrap', { 'no-image': !primaryImage })}>
        {primaryImage ? (
          <img src={primaryImage} alt={product.displayName} loading="lazy" />
        ) : (
          <div className="placeholder">No image</div>
        )}
      </div>
      <div className="product-body">
        <h2>{product.displayName}</h2>
        {product.category && <div className="category">{product.category}</div>}
        {product.price && (
          <div className="price">
            {product.currency ? `${product.currency} ` : ''}
            {product.price}
          </div>
        )}
        <ProductGallery product={product} />
        <ProductDetails product={product} />
      </div>
    </article>
  )
}

ProductCard.propTypes = {
  product: PropTypes.object.isRequired,
}
