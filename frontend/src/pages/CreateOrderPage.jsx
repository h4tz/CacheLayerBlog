import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useRail } from '../context/RailContext'
import { productsApi } from '../api/products'
import { ordersApi } from '../api/orders'
import ErrorAlert from '../components/ErrorAlert'

export default function CreateOrderPage() {
  const { rail } = useRail()
  const navigate = useNavigate()
  const [products, setProducts] = useState([])
  const [lines, setLines] = useState([{ product_sku: '', quantity: 1 }])
  const [note, setNote] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    productsApi.list(rail, { page_size: 100 })
      .then((res) => setProducts(res.data.items))
      .catch(setError)
      .finally(() => setFetching(false))
  }, [rail])

  const addLine = () => {
    setLines([...lines, { product_sku: '', quantity: 1 }])
  }

  const removeLine = (idx) => {
    setLines(lines.filter((_, i) => i !== idx))
  }

  const updateLine = (idx, field, value) => {
    const updated = [...lines]
    updated[idx] = { ...updated[idx], [field]: value }
    setLines(updated)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    const validLines = lines.filter((l) => l.product_sku && l.quantity > 0)
    if (validLines.length === 0) {
      setError(new Error('Add at least one product'))
      return
    }
    setLoading(true)
    try {
      const res = await ordersApi.create(rail, {
        lines: validLines.map((l) => ({
          product_sku: l.product_sku,
          quantity: parseInt(l.quantity, 10),
        })),
        note,
      })
      navigate(`/orders/${res.data.id}`)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Place New Order</h1>

      <ErrorAlert error={error} />

      {fetching ? (
        <div className="text-center py-8 text-gray-500">Loading products...</div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="bg-white rounded-lg shadow p-6 mb-4">
            <h2 className="text-lg font-semibold mb-4">Order Items</h2>
            {lines.map((line, idx) => (
              <div key={idx} className="flex gap-2 mb-3 items-center">
                <select
                  value={line.product_sku}
                  onChange={(e) => updateLine(idx, 'product_sku', e.target.value)}
                  required
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select product...</option>
                  {products.map((p) => (
                    <option key={p.sku} value={p.sku}>
                      {p.sku} — {p.name} (${p.price}) [stock: {p.stock}]
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  min="1"
                  value={line.quantity}
                  onChange={(e) => updateLine(idx, 'quantity', e.target.value)}
                  className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {lines.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeLine(idx)}
                    className="text-red-500 hover:text-red-700 px-2"
                  >
                    &#10005;
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={addLine}
              className="text-sm text-blue-600 hover:underline"
            >
              + Add another item
            </button>
          </div>

          <div className="bg-white rounded-lg shadow p-6 mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Note (optional)</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Any special instructions..."
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {loading ? 'Placing order...' : 'Place Order'}
          </button>
        </form>
      )}
    </div>
  )
}
