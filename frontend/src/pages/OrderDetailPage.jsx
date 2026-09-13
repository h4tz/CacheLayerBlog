import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useRail } from '../context/RailContext'
import { useAuth } from '../context/AuthContext'
import { ordersApi } from '../api/orders'
import ErrorAlert from '../components/ErrorAlert'

const STATUSES = ['pending', 'paid', 'shipped', 'cancelled']

export default function OrderDetailPage() {
  const { id } = useParams()
  const { rail } = useRail()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updating, setUpdating] = useState(false)

  const isStaff = user?.role === 'admin' || user?.role === 'staff'

  const fetchOrder = () => {
    ordersApi.get(rail, id)
      .then((res) => setOrder(res.data))
      .catch(setError)
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchOrder() }, [rail, id])

  const handleStatusChange = async (newStatus) => {
    setUpdating(true)
    setError(null)
    try {
      const res = await ordersApi.updateStatus(rail, id, newStatus)
      setOrder(res.data)
    } catch (err) {
      setError(err)
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <div className="p-8 text-center text-gray-500">Loading...</div>
  if (error && !order) return <div className="p-8"><ErrorAlert error={error} /></div>

  return (
    <div className="max-w-3xl mx-auto p-6">
      <button onClick={() => navigate('/orders')} className="text-blue-600 hover:underline mb-4 inline-block">
        &larr; Back to Orders
      </button>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Order #{order.id}</h1>
            <p className="text-gray-500 text-sm mt-1">
              {order.items?.length || 0} item(s)
            </p>
          </div>
          <StatusBadge status={order.status} />
        </div>

        <ErrorAlert error={error} />

        {order.note && (
          <div className="mb-4 p-3 bg-gray-50 rounded-md">
            <p className="text-sm text-gray-500">Note</p>
            <p className="text-gray-700">{order.note}</p>
          </div>
        )}

        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3">Items</h2>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Qty</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Line Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {order.items?.map((item, idx) => (
                <tr key={idx}>
                  <td className="px-4 py-3 font-mono text-sm">{item.product_sku}</td>
                  <td className="px-4 py-3">{item.quantity}</td>
                  <td className="px-4 py-3">${item.unit_price}</td>
                  <td className="px-4 py-3 font-medium">${item.line_total}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t-2 border-gray-300">
                <td colSpan={3} className="px-4 py-3 text-right font-semibold">Total</td>
                <td className="px-4 py-3 font-bold text-lg">${order.total}</td>
              </tr>
            </tfoot>
          </table>
        </div>

        {isStaff && (
          <div className="border-t pt-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Update Status</p>
            <div className="flex gap-2">
              {STATUSES.map((s) => (
                <button
                  key={s}
                  onClick={() => handleStatusChange(s)}
                  disabled={updating || order.status === s}
                  className={`px-3 py-1 text-sm rounded-md border disabled:opacity-50 ${
                    order.status === s
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
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
    <span className={`px-3 py-1 text-sm font-medium rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  )
}
