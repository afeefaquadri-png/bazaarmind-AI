import { useState, useEffect } from 'react'
import { useShop } from '../hooks/useShop.jsx'
import { analyticsApi } from '../services/api.js'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend
} from 'recharts'
import { Package, ShoppingCart, TrendingUp, AlertTriangle, MessageSquare, IndianRupee } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const CHART_COLORS = ['#0ea5e9', '#06d6a0', '#ffd166', '#ff6b6b', '#a78bfa']

function StatCard({ label, value, sub, icon: Icon, color, onClick }) {
  return (
    <div className={`stat-card cursor-pointer hover:shadow-md transition-all ${onClick ? 'hover:-translate-y-0.5' : ''}`} onClick={onClick}>
      <div className={`stat-icon ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-surface-900">{value ?? '—'}</p>
        <p className="text-sm font-medium text-surface-700">{label}</p>
        {sub && <p className="text-xs text-surface-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { currentShop } = useShop()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [salesData, setSalesData] = useState([])
  const [topProducts, setTopProducts] = useState([])
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!currentShop?.id) { setLoading(false); return }
    const load = async () => {
      setLoading(true)
      try {
        const [s, sales, top, ch] = await Promise.all([
          analyticsApi.dashboard(currentShop.id),
          analyticsApi.salesChart(currentShop.id, 7),
          analyticsApi.topProducts(currentShop.id),
          analyticsApi.channels(currentShop.id),
        ])
        setStats(s.data)
        setSalesData(sales.data)
        setTopProducts(top.data)
        setChannels(ch.data)
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [currentShop?.id])

  if (!currentShop) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-4 p-8 text-center">
        <div className="text-6xl">🏪</div>
        <h2 className="text-2xl font-bold text-surface-900">Welcome to BazaarMind AI</h2>
        <p className="text-surface-500 max-w-sm">Create your first shop to start managing inventory, orders, and AI-powered insights.</p>
        <button className="btn-primary" onClick={() => navigate('/shops')}>Create Your First Shop</button>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900">Dashboard</h1>
          <p className="text-surface-500 text-sm mt-0.5">
            {currentShop.template?.icon} {currentShop.name} — {currentShop.template?.label}
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary text-sm" onClick={() => navigate('/products')}>+ Add Product</button>
          <button className="btn-primary text-sm" onClick={() => navigate('/orders')}>New Order</button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-24 rounded-2xl" />)}
        </div>
      ) : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Total Products"   value={stats?.total_products}   icon={Package}       color="bg-brand-600"   onClick={() => navigate('/products')} />
            <StatCard label="Today's Orders"   value={stats?.today_orders}     sub={`${stats?.total_orders} total`} icon={ShoppingCart} color="bg-emerald-500" onClick={() => navigate('/orders')} />
            <StatCard label="Today's Revenue"  value={`₹${stats?.today_revenue?.toFixed(0)}`} sub={`₹${stats?.total_revenue?.toFixed(0)} total`} icon={IndianRupee} color="bg-amber-500" />
            <StatCard label="Low Stock Items"  value={stats?.low_stock_count}  icon={AlertTriangle} color="bg-red-500"     onClick={() => navigate('/products')} />
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Sales Chart */}
            <div className="col-span-2 card">
              <h3 className="font-semibold text-surface-800 mb-4">Revenue Last 7 Days</h3>
              {salesData.length === 0 ? (
                <div className="h-48 flex items-center justify-center text-surface-400 text-sm">No sales data yet</div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={salesData} barSize={28}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} tickFormatter={v => `₹${v}`} />
                    <Tooltip formatter={(v) => [`₹${v}`, 'Revenue']} contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 24px rgba(0,0,0,0.1)' }} />
                    <Bar dataKey="revenue" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Channel Breakdown */}
            <div className="card">
              <h3 className="font-semibold text-surface-800 mb-4">Order Channels</h3>
              {channels.length === 0 ? (
                <div className="h-48 flex items-center justify-center text-surface-400 text-sm">No orders yet</div>
              ) : (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={channels} dataKey="count" nameKey="channel" cx="50%" cy="50%" outerRadius={70} label={({ channel, percent }) => `${channel} ${(percent*100).toFixed(0)}%`} labelLine={false}>
                      {channels.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Top Products */}
            <div className="col-span-2 card">
              <h3 className="font-semibold text-surface-800 mb-4">Top Products by Sales</h3>
              {topProducts.length === 0 ? (
                <div className="text-surface-400 text-sm text-center py-8">No product data yet</div>
              ) : (
                <div className="space-y-3">
                  {topProducts.map((p, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center flex-shrink-0">{i+1}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-center mb-1">
                          <p className="text-sm font-medium text-surface-800 truncate">{p.name}</p>
                          <p className="text-sm font-semibold text-surface-900 ml-2">₹{p.revenue}</p>
                        </div>
                        <div className="h-1.5 bg-surface-100 rounded-full">
                          <div className="h-1.5 rounded-full bg-brand-500" style={{ width: `${(p.qty / topProducts[0].qty) * 100}%` }} />
                        </div>
                        <p className="text-xs text-surface-400 mt-0.5">{p.qty} units sold</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* WhatsApp Stats */}
            <div className="card flex flex-col justify-between">
              <h3 className="font-semibold text-surface-800 mb-4">WhatsApp Bot</h3>
              <div className="text-center py-4">
                <div className="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <MessageSquare size={24} className="text-emerald-600" />
                </div>
                <p className="text-3xl font-bold text-surface-900">{stats?.whatsapp_orders ?? 0}</p>
                <p className="text-sm text-surface-500 mt-1">Orders via WhatsApp</p>
              </div>
              <button className="btn-secondary w-full text-sm" onClick={() => navigate('/whatsapp')}>
                Test Bot Simulator →
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
