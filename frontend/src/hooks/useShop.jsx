import { createContext, useContext, useState, useEffect } from 'react'
import { shopApi } from '../services/api'

const ShopContext = createContext(null)

export function ShopProvider({ children }) {
  const [shops, setShops] = useState([])
  const [currentShop, setCurrentShop] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadShops = async () => {
    try {
      const { data } = await shopApi.list()
      setShops(data)
      // Auto-select first shop or restore from localStorage
      const savedId = localStorage.getItem('bazaarmind_shop_id')
      const found = data.find(s => s.id === savedId) || data[0]
      if (found) setCurrentShop(found)
    } catch (e) {
      console.error('Failed to load shops', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadShops() }, [])

  const selectShop = (shop) => {
    setCurrentShop(shop)
    if (shop?.id) localStorage.setItem('bazaarmind_shop_id', shop.id)
  }

  const addShop = (shop) => {
    setShops(prev => [...prev, shop])
    selectShop(shop)
  }

  const removeShop = (id) => {
    setShops(prev => prev.filter(s => s.id !== id))
    if (currentShop?.id === id) {
      const remaining = shops.filter(s => s.id !== id)
      setCurrentShop(remaining[0] || null)
    }
  }

  return (
    <ShopContext.Provider value={{ shops, currentShop, loading, selectShop, addShop, removeShop, refresh: loadShops }}>
      {children}
    </ShopContext.Provider>
  )
}

export function useShop() {
  const ctx = useContext(ShopContext)
  if (!ctx) throw new Error('useShop must be used inside ShopProvider')
  return ctx
}
