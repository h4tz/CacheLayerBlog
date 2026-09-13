import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useRail } from '../context/RailContext'
import { useAuth } from '../context/AuthContext'
import { productsApi } from '../api/products'
import ErrorAlert from '../components/ErrorAlert'

export default function ProductDetailPage() {
  const { sku } = useParams()
  const { rail } = useRail()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stockValue, setStockValue] = useState('')
  const [updating, setUpdating] = useState(false)

  const isStaff = user?.role === 'admin' || user?.role === 'staff'

  useEffect(() => {
    productsApi.get(rail, sku)
      .then((res) => {
        setProduct(res.data)
        setStockValue(String(res.data.stock))
      })
      .catch(setError)
      .finally(() => setLoading(false))
  }, [rail, sku])

  const handleStockUpdate = async (e) => {
    e.preventDefault()
    setUpdating(true)
    setError(null)
    try {
      const res = await productsApi.updateStock(rail, sku, parseInt(stockValue, 10))
      setProduct(res.data)
    } catch (err) {
      setError(err)
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <div className="p-8 text-center text-gray-500">Loading...</div>
  if (error && !product) return <div className="p-8"><ErrorAlert error={error} /></div>

  return (
    <div className="max-w-3xl mx-auto p-6">
      <button onClick={() => navigate('/products')} className="text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Products
      </button>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">{product.name}</h1>
            <p className="text-gray-500 font-mono text-sm">{product.sku}</p>
          </div>
          <span className={`px-3 py-1 text-sm rounded-full ${product.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500'}`}>
            {product.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>

        <ErrorAlert error={error} />

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <p className="text-sm text-gray-500">Category</p>
            <p className="font-medium">{product.category}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Price</p>
            <p className="text-xl font-bold">${product.price}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Stock</p>
            <p className={`text-xl font-bold ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {product.stock}
            </p>
          </div>
        </div>

        {product.description && (
          <div className="mb-6">
            <p className="text-sm text-gray-500 mb-1">Description</p>
            <p className="text-gray-700">{product.description}</p>
          </div>
        )}

        {isStaff && (
          <form onSubmit={handleStockUpdate} className="border-t pt-4 mt-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Update Stock</p>
            <div className="flex gap-2">
              <input
                type="number"
                value={stockValue}
                onChange={(e) => setStockValue(e.target.value)}
                className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={updating}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {updating ? 'Updating...' : 'Update'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
