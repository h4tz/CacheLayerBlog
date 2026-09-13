import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ProductsPage from './pages/ProductsPage'
import ProductDetailPage from './pages/ProductDetailPage'
import OrdersPage from './pages/OrdersPage'
import OrderDetailPage from './pages/OrderDetailPage'
import CreateOrderPage from './pages/CreateOrderPage'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/products" element={<ProtectedRoute><ProductsPage /></ProtectedRoute>} />
        <Route path="/products/:sku" element={<ProtectedRoute><ProductDetailPage /></ProtectedRoute>} />
        <Route path="/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
        <Route path="/orders/new" element={<ProtectedRoute><CreateOrderPage /></ProtectedRoute>} />
        <Route path="/orders/:id" element={<ProtectedRoute><OrderDetailPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
