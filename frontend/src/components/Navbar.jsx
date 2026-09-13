import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import RailToggle from './RailToggle'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link to="/" className="text-xl font-bold text-blue-600">
            CacheLayer
          </Link>
          {user && (
            <div className="flex items-center gap-4">
              <Link to="/products" className="text-gray-600 hover:text-gray-900">
                Products
              </Link>
              <Link to="/orders" className="text-gray-600 hover:text-gray-900">
                Orders
              </Link>
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          {user && <RailToggle />}
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">
                {user.email}
                <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-gray-100">
                  {user.role}
                </span>
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link to="/login" className="text-sm text-gray-600 hover:text-gray-900">
                Login
              </Link>
              <Link
                to="/register"
                className="text-sm px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
