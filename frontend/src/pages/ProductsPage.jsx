import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useRail } from '../context/RailContext'
import { useAuth } from '../context/AuthContext'
import { productsApi } from '../api/products'
import Pagination from '../components/Pagination'
import ErrorAlert from '../components/ErrorAlert'

export default function ProductsPage() {
  const { rail } = useRail()
  const { user } = useAuth()
  const [products, setProducts] = useState([])
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState({ sku: '', name: '', category: '', price: '', stock: '0', description: '' })
  const [creating, setCreating] = useState(false)

  const fetchProducts = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { page, page_size: 10 }
      if (search) params.search = search
      const res = await productsApi.list(rail, params)
      setProducts(res.data.items)
      setMeta(res.data.meta)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [rail, page, search])

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    fetchProducts()
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    try {
      await productsApi.create(rail, {
        ...createForm,
        price: parseFloat(createForm.price),
        stock: parseInt(createForm.stock, 10),
      })
      setShowCreate(false)
      setCreateForm({ sku: '', name: '', category: '', price: '', stock: '0', description: '' })
      fetchProducts()
    } catch (err) {
      setError(err)
    } finally {
      setCreating(false)
    }
  }

  const isStaff = user?.role === 'admin' || user?.role === 'staff'

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Products</h1>
        {isStaff && (
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
          >
            {showCreate ? 'Cancel' : '+ New Product'}
          </button>
        )}
      </div>

      <ErrorAlert error={error} />

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-white rounded-lg shadow p-6 mb-6 space-y-4">
          <h2 className="text-lg font-semibold">Create Product</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              placeholder="SKU"
              required
              value={createForm.sku}
              onChange={(e) => setCreateForm({ ...createForm, sku: e.target.value })}
              className="px-3 py-2 border rounded-md"
            />
            <input
              placeholder="Name"
              required
              value={createForm.name}
              onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
              className="px-3 py-2 border rounded-md"
            />
            <input
              placeholder="Category"
              required
              value={createForm.category}
              onChange={(e) => setCreateForm({ ...createForm, category: e.target.value })}
              className="px-3 py-2 border rounded-md"
            />
            <input
              placeholder="Price"
              type="number"
              step="0.01"
              required
              value={createForm.price}
              onChange={(e) => setCreateForm({ ...createForm, price: e.target.value })}
              className="px-3 py-2 border rounded-md"
            />
            <input
              placeholder="Stock"
              type="number"
              value={createForm.stock}
              onChange={(e) => setCreateForm({ ...createForm, stock: e.target.value })}
              className="px-3 py-2 border rounded-md"
            />
            <input
              placeholder="Description"
              value={createForm.description}
              onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
              className="px-3 py-2 border rounded-md"
            />
          </div>
          <button
            type="submit"
            disabled={creating}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {creating ? 'Creating...' : 'Create'}
          </button>
        </form>
      )}

      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
        >
          Search
        </button>
      </form>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : products.length === 0 ? (
        <div className="text-center py-8 text-gray-400">No products found</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <Link to={`/products/${product.sku}`} className="text-blue-600 hover:underline font-mono text-sm">
                        {product.sku}
                      </Link>
                    </td>
                    <td className="px-6 py-4 font-medium">{product.name}</td>
                    <td className="px-6 py-4 text-gray-500">{product.category}</td>
                    <td className="px-6 py-4 font-medium">${product.price}</td>
                    <td className="px-6 py-4">
                      <span className={product.stock > 0 ? 'text-green-600' : 'text-red-600'}>
                        {product.stock}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${product.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500'}`}>
                        {product.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination meta={meta} onPageChange={setPage} />
        </>
      )}
    </div>
  )
}
