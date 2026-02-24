import { Routes, Route, Navigate } from 'react-router-dom'
import { ShopProvider } from './hooks/useShop.jsx'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Products from './pages/Products.jsx'
import Orders from './pages/Orders.jsx'
import Shops from './pages/Shops.jsx'
import WhatsApp from './pages/WhatsApp.jsx'

export default function App() {
  return (
    <ShopProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="products" element={<Products />} />
          <Route path="orders" element={<Orders />} />
          <Route path="shops" element={<Shops />} />
          <Route path="whatsapp" element={<WhatsApp />} />
        </Route>
      </Routes>
    </ShopProvider>
  )
}
