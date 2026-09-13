import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useRail } from '../context/RailContext'
import { productsApi } from '../api/products'
import { ordersApi } from '../api/orders'

export default function DashboardPage() {
  const { user } = useAuth()
  const { rail } = useRail()
  const [stats, setStats] = useState({ products: 0, orders: 0, recentOrders: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [prodRes, orderRes] = await Promise.all([
          productsApi.list(rail, { page_size: 1 }),
          ordersApi.list(rail, { page_size: 5 }),
        ])
        setStats({
          products: prodRes.data.meta.total,
          orders: orderRes.data.meta.total,
          recentOrders: orderRes.data.items,
        })
      } catch (err) {
        console.error('Failed to load dashboard', err)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [rail])

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading dashboard...</div>
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-500">Welcome back, {user?.email}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500">Active Rail</p>
          <p className={`text-2xl font-bold ${rail === 'drf' ? 'text-blue-600' : 'text-purple-600'}`}>
            {rail.toUpperCase()}
          </p>
        </div>
        <Link to="/products" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition">
          <p className="text-sm text-gray-500">Products</p>
          <p className="text-2xl font-bold">{stats.products}</p>
        </Link>
        <Link to="/orders" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition">
          <p className="text-sm text-gray-500">Orders</p>
          <p className="text-2xl font-bold">{stats.orders}</p>
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent Orders</h2>
          <Link to="/orders" className="text-sm text-blue-600 hover:underline">View all</Link>
        </div>
        {stats.recentOrders.length === 0 ? (
          <div className="p-6 text-center text-gray-400">No orders yet</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {stats.recentOrders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link to={`/orders/${order.id}`} className="text-blue-600 hover:underline">
                      #{order.id}
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={order.status} />
                  </td>
                  <td className="px-6 py-4 font-medium">${order.total}</td>
                  <td className="px-6 py-4 text-gray-500">{order.items?.length || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
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
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  )
}
