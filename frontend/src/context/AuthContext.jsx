import { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '../api/auth'
import { useRail } from './RailContext'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const { rail } = useRail()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      authApi.me(rail)
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [rail])

  const login = async (email, password) => {
    const res = await authApi.login(rail, { email, password })
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    const meRes = await authApi.me(rail)
    setUser(meRes.data)
    return meRes.data
  }

  const register = async (email, username, password) => {
    await authApi.register(rail, { email, username, password })
    return await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
