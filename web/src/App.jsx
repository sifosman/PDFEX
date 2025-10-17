import { useEffect, useMemo, useState } from 'react'
import { supabase } from './supabaseClient'
import ProductCard from './components/ProductCard'

const PAGE_LIMIT = 48

export default function App() {
  const [products, setProducts] = useState([])
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [hasMore, setHasMore] = useState(true)

  useEffect(() => {
    fetchPage(0, true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function fetchPage(pageNumber, replace = false) {
    try {
      setLoading(true)
      const from = pageNumber * PAGE_LIMIT
      const to = from + PAGE_LIMIT - 1
      const { data, error: fetchError } = await supabase
        .from('products')
        .select(
          `product_code,name,subtitle,category,pack_quantity,price,currency,spec_features,dimensions,primary_image_url,image_urls`
        )
        .order('product_code', { ascending: true })
        .range(from, to)

      if (fetchError) throw fetchError

      if (!data || data.length === 0) {
        setHasMore(false)
        if (replace) {
          setProducts([])
        }
        return
      }

      const normalized = data.map((product) => {
        const imageUrls = Array.isArray(product.image_urls)
          ? product.image_urls
          : typeof product.image_urls === 'string'
          ? [product.image_urls]
          : []
        const specFeatures = Array.isArray(product.spec_features)
          ? product.spec_features
          : typeof product.spec_features === 'string'
          ? [product.spec_features]
          : []
        const displayName = [product.name, product.subtitle]
          .filter(Boolean)
          .join(' – ')

        return {
          ...product,
          displayName: displayName || product.product_code,
          image_urls: imageUrls,
          spec_features: specFeatures,
        }
      })

      if (replace) {
        setProducts(normalized)
      } else {
        setProducts((prev) => [...prev, ...normalized])
      }
      setPage(pageNumber)
      setHasMore(data.length === PAGE_LIMIT)
    } catch (err) {
      console.error(err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filteredProducts = useMemo(() => {
    if (!search.trim()) return products
    const term = search.toLowerCase()
    return products.filter((product) => {
      return (
        product.displayName.toLowerCase().includes(term) ||
        (product.product_code && product.product_code.toLowerCase().includes(term)) ||
        (product.category && product.category.toLowerCase().includes(term))
      )
    })
  }, [products, search])

  const showLoadMore = hasMore && !loading && filteredProducts.length === products.length

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>PDFEX Shop</h1>
        <p className="tagline">Browse catalogue products synced from Supabase</p>
        <div className="toolbar">
          <input
            type="search"
            placeholder="Search by name, subtitle, or code"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main>
        {filteredProducts.length === 0 && !loading ? (
          <div className="empty-state">No products matched your search.</div>
        ) : (
          <section className="product-grid">
            {filteredProducts.map((product) => (
              <ProductCard key={product.product_code} product={product} />
            ))}
          </section>
        )}

        {loading && <div className="loading">Loading products…</div>}

        {showLoadMore && (
          <div className="load-more">
            <button onClick={() => fetchPage(page + 1)}>Load more</button>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by Supabase · Catalogue importer: PDFEX</p>
      </footer>
    </div>
  )
}
