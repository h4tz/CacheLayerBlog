import { createContext, useContext, useState } from 'react'

const RailContext = createContext()

export function RailProvider({ children }) {
  const [rail, setRail] = useState(() => localStorage.getItem('rail') || 'drf')

  const switchRail = (newRail) => {
    setRail(newRail)
    localStorage.setItem('rail', newRail)
  }

  return (
    <RailContext.Provider value={{ rail, switchRail }}>
      {children}
    </RailContext.Provider>
  )
}

export function useRail() {
  const ctx = useContext(RailContext)
  if (!ctx) throw new Error('useRail must be used within RailProvider')
  return ctx
}
