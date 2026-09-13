import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useRail } from '../context/RailContext'
import { useAuth } from '../context/AuthContext'
import { ordersApi } from '../api/orders'
import Pagination from '../components/Pagination'
import ErrorAlert from '../components/ErrorAlert'

export default function OrdersPage() {
  const { rail } = useRail()
  const { user } = useAuth()
  const [orders, setOrders] = useState([])
  const [meta, setMeta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)

  useEffect(() => {
    setLoading(true)
    ordersApi.list(rail, { page, page_size: 10 })
      .then((res) => {
        setOrders(res.data.items)
        setMeta(res.data.meta)
      })
      .catch(setError)
      .finally(() => setLoading(false))
  }, [rail, page])

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Orders</h1>
        <Link
          to="/orders/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
        >
          + New Order
        </Link>
      </div>

      <ErrorAlert error={error} />

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : orders.length === 0 ? (
        <div className="text-center py-8 text-gray-400">No orders yet</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Note</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {orders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <Link to={`/orders/${order.id}`} className="text-blue-600 hover:underline font-mono">
                        #{order.id}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={order.status} />
                    </td>
                    <td className="px-6 py-4 font-medium">${order.total}</td>
                    <td className="px-6 py-4 text-gray-500">{order.items?.length || 0}</td>
                    <td className="px-6 py-4 text-gray-400 text-sm truncate max-w-[200px]">
                      {order.note || '—'}
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

function StatusBadge({ status }) {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    paid: 'bg-blue-100 text-blue-800',
    shipped: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  }
  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  )
}
