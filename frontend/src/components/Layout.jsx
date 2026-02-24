import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useShop } from '../hooks/useShop.jsx'
import {
  LayoutDashboard, Package, ShoppingCart, Store, MessageSquare,
  ChevronDown, Plus, Zap, AlertTriangle
} from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/products',  icon: Package,         label: 'Products' },
  { to: '/orders',    icon: ShoppingCart,    label: 'Orders' },
  { to: '/whatsapp',  icon: MessageSquare,   label: 'WhatsApp Bot' },
  { to: '/shops',     icon: Store,           label: 'Shops' },
]

export default function Layout() {
  const { shops, currentShop, selectShop } = useShop()
  const [shopOpen, setShopOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <div className="flex h-screen overflow-hidden bg-surface-50">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 bg-white border-r border-surface-200 flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-5 border-b border-surface-200">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
              <Zap size={16} className="text-white" />
            </div>
            <div>
              <p className="font-bold text-surface-900 text-sm leading-none">BazaarMind</p>
              <p className="text-xs text-surface-400 leading-none mt-0.5">AI Platform</p>
            </div>
          </div>
        </div>

        {/* Shop Selector */}
        <div className="p-3 border-b border-surface-100">
          <div className="relative">
            <button
              onClick={() => setShopOpen(p => !p)}
              className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-surface-50 hover:bg-surface-100 transition-colors text-left"
            >
              <span className="text-xl leading-none">
                {currentShop?.template?.icon || '🏪'}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-surface-900 truncate">
                  {currentShop?.name || 'Select Shop'}
                </p>
                <p className="text-xs text-surface-400 capitalize">
                  {currentShop?.shop_type?.replace('_', ' ') || 'No shop selected'}
                </p>
              </div>
              <ChevronDown size={14} className={`text-surface-400 transition-transform ${shopOpen ? 'rotate-180' : ''}`} />
            </button>

            {shopOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-surface-200 rounded-xl shadow-lg z-50 overflow-hidden">
                <div className="max-h-48 overflow-y-auto">
                  {shops.map(shop => (
                    <button
                      key={shop.id}
                      onClick={() => { selectShop(shop); setShopOpen(false) }}
                      className={`w-full flex items-center gap-2.5 px-3 py-2.5 text-left hover:bg-surface-50 transition-colors text-sm
                        ${currentShop?.id === shop.id ? 'bg-brand-50 text-brand-700' : 'text-surface-700'}`}
                    >
                      <span>{shop.template?.icon || '🏪'}</span>
                      <div className="min-w-0">
                        <p className="font-medium truncate">{shop.name}</p>
                        <p className="text-xs text-surface-400 capitalize">{shop.shop_type?.replace('_', ' ')}</p>
                      </div>
                    </button>
                  ))}
                </div>
                <div className="border-t border-surface-100">
                  <button
                    onClick={() => { navigate('/shops'); setShopOpen(false) }}
                    className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-brand-600 hover:bg-brand-50 transition-colors font-medium"
                  >
                    <Plus size={14} /> Add new shop
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-0.5">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-surface-100">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-3">
            <div className="flex items-start gap-2">
              <AlertTriangle size={14} className="text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs font-semibold text-amber-800">MVP Mode</p>
                <p className="text-xs text-amber-600 mt-0.5">Connect MongoDB + Twilio for full features</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {!currentShop && (
          <div className="bg-brand-600 text-white text-center py-2 text-sm font-medium">
            👋 Welcome! <button onClick={() => navigate('/shops')} className="underline">Create your first shop</button> to get started.
          </div>
        )}
        <Outlet />
      </main>
    </div>
  )
}
