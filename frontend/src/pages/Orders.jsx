import { useState, useEffect } from 'react'
import { useShop } from '../hooks/useShop.jsx'
import { orderApi, productApi } from '../services/api.js'
import Modal from '../components/Modal.jsx'
import { Plus, ShoppingCart, Trash2, ChevronDown } from 'lucide-react'

const STATUS_COLORS = {
  confirmed: 'badge-green',
  pending: 'badge-yellow',
  delivered: 'badge-blue',
  cancelled: 'badge-red',
}

const CHANNEL_ICONS = {
  whatsapp: '💬',
  manual: '🖐️',
  app: '📱',
}

export default function Orders() {
  const { currentShop } = useShop()
  const [orders, setOrders] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ customer_name: '', customer_phone: '', notes: '' })
  const [orderItems, setOrderItems] = useState([{ product_id: '', quantity: 1 }])
  const [saving, setSaving] = useState(false)
  const [expandedOrder, setExpandedOrder] = useState(null)

  const load = async () => {
    if (!currentShop?.id) { setLoading(false); return }
    setLoading(true)
    try {
      const [o, p] = await Promise.all([
        orderApi.list(currentShop.id, { limit: 100 }),
        productApi.list(currentShop.id),
      ])
      setOrders(o.data)
      setProducts(p.data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  useEffect(() => { load() }, [currentShop?.id])

  const addItem = () => setOrderItems(p => [...p, { product_id: '', quantity: 1 }])
  const removeItem = (i) => setOrderItems(p => p.filter((_, idx) => idx !== i))
  const updateItem = (i, field, value) => {
    setOrderItems(p => {
      const next = [...p]
      next[i] = { ...next[i], [field]: value }
      return next
    })
  }

  const getProduct = (id) => products.find(p => p.id === id)
  const orderTotal = orderItems.reduce((sum, item) => {
    const p = getProduct(item.product_id)
    return sum + (p ? p.price * (item.quantity || 0) : 0)
  }, 0)

  const handleCreate = async () => {
    const validItems = orderItems.filter(i => i.product_id && i.quantity > 0)
    if (!validItems.length) { alert('Add at least one product'); return }
    setSaving(true)
    try {
      const items = validItems.map(i => {
        const p = getProduct(i.product_id)
        return {
          product_id: i.product_id,
          product_name: p.name,
          quantity: parseInt(i.quantity),
          unit_price: p.price,
          total: p.price * i.quantity,
        }
      })
      await orderApi.create({
        shop_id: currentShop.id,
        customer_name: form.customer_name || 'Walk-in Customer',
        customer_phone: form.customer_phone,
        notes: form.notes,
        channel: 'manual',
        items,
      })
      setShowModal(false)
      setForm({ customer_name: '', customer_phone: '', notes: '' })
      setOrderItems([{ product_id: '', quantity: 1 }])
      load()
    } catch (e) { alert(e.response?.data?.detail || 'Failed to create order') }
    setSaving(false)
  }

  const updateStatus = async (id, status) => {
    await orderApi.updateStatus(id, status)
    load()
  }

  if (!currentShop) return (
    <div className="h-full flex items-center justify-center text-surface-400">
      <p>Please select a shop first.</p>
    </div>
  )

  return (
    <div className="p-6 space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-surface-900">Orders</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowModal(true)}>
          <Plus size={16} /> New Order
        </button>
      </div>

      {loading ? (
        <div className="space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="skeleton h-16 rounded-xl" />)}</div>
      ) : orders.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-16 text-surface-400 gap-3">
          <ShoppingCart size={40} strokeWidth={1.5} />
          <p className="text-sm">No orders yet. Create your first order!</p>
          <button className="btn-primary text-sm" onClick={() => setShowModal(true)}>+ New Order</button>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <table className="w-full">
            <thead className="bg-surface-50 border-b border-surface-100">
              <tr>
                <th className="table-header">Order</th>
                <th className="table-header">Customer</th>
                <th className="table-header">Channel</th>
                <th className="table-header">Total</th>
                <th className="table-header">Status</th>
                <th className="table-header">Date</th>
                <th className="table-header">Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(order => (
                <>
                  <tr key={order.id} className="table-row">
                    <td className="table-cell">
                      <button
                        onClick={() => setExpandedOrder(expandedOrder === order.id ? null : order.id)}
                        className="flex items-center gap-1.5 font-mono text-xs text-surface-500 hover:text-brand-600 transition-colors"
                      >
                        <ChevronDown size={12} className={`transition-transform ${expandedOrder === order.id ? 'rotate-180' : ''}`} />
                        #{order.id.slice(-6).toUpperCase()}
                      </button>
                    </td>
                    <td className="table-cell">
                      <p className="font-medium text-surface-800">{order.customer_name}</p>
                      {order.customer_phone && <p className="text-xs text-surface-400">{order.customer_phone}</p>}
                    </td>
                    <td className="table-cell">
                      <span>{CHANNEL_ICONS[order.channel] || '📋'} {order.channel}</span>
                    </td>
                    <td className="table-cell font-bold text-surface-900">₹{order.total_amount}</td>
                    <td className="table-cell">
                      <span className={`badge ${STATUS_COLORS[order.status] || 'badge-gray'}`}>{order.status}</span>
                    </td>
                    <td className="table-cell text-surface-400 text-xs">
                      {new Date(order.created_at).toLocaleDateString('en-IN')}
                    </td>
                    <td className="table-cell">
                      <select
                        className="text-xs border border-surface-200 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/30"
                        value={order.status}
                        onChange={e => updateStatus(order.id, e.target.value)}
                      >
                        {['pending','confirmed','delivered','cancelled'].map(s => <option key={s} value={s}>{s}</option>)}
                      </select>
                    </td>
                  </tr>
                  {expandedOrder === order.id && (
                    <tr key={`${order.id}-detail`}>
                      <td colSpan={7} className="px-4 pb-3 bg-surface-50">
                        <div className="space-y-1.5">
                          {order.items.map((item, i) => (
                            <div key={i} className="flex items-center justify-between text-sm bg-white rounded-lg px-3 py-2 border border-surface-100">
                              <span className="font-medium text-surface-700">{item.product_name}</span>
                              <span className="text-surface-500">{item.quantity} × ₹{item.unit_price} = <strong className="text-surface-900">₹{item.total}</strong></span>
                            </div>
                          ))}
                          {order.notes && <p className="text-xs text-surface-400 px-1">Note: {order.notes}</p>}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Order Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create New Order" size="lg">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Customer Name</label>
              <input className="input" placeholder="Walk-in Customer" value={form.customer_name} onChange={e => setForm(p => ({ ...p, customer_name: e.target.value }))} />
            </div>
            <div>
              <label className="label">Phone (optional)</label>
              <input className="input" placeholder="+91 99999 99999" value={form.customer_phone} onChange={e => setForm(p => ({ ...p, customer_phone: e.target.value }))} />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="label mb-0">Order Items</label>
              <button onClick={addItem} className="text-xs text-brand-600 font-medium hover:underline">+ Add Item</button>
            </div>
            <div className="space-y-2">
              {orderItems.map((item, i) => {
                const p = getProduct(item.product_id)
                return (
                  <div key={i} className="flex items-center gap-2">
                    <select
                      className="input flex-1"
                      value={item.product_id}
                      onChange={e => updateItem(i, 'product_id', e.target.value)}
                    >
                      <option value="">Select product...</option>
                      {products.map(p => (
                        <option key={p.id} value={p.id}>{p.name} (Stock: {p.stock})</option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min="1"
                      className="input w-20"
                      value={item.quantity}
                      onChange={e => updateItem(i, 'quantity', e.target.value)}
                    />
                    {p && <span className="text-sm font-semibold text-surface-700 w-20 text-right">₹{(p.price * item.quantity).toFixed(0)}</span>}
                    <button onClick={() => removeItem(i)} className="p-1.5 text-red-400 hover:text-red-600 transition-colors">
                      <Trash2 size={14} />
                    </button>
                  </div>
                )
              })}
            </div>
          </div>

          {orderTotal > 0 && (
            <div className="bg-brand-50 border border-brand-200 rounded-xl p-3 flex justify-between items-center">
              <span className="font-semibold text-brand-800">Total Amount</span>
              <span className="text-xl font-bold text-brand-700">₹{orderTotal.toFixed(2)}</span>
            </div>
          )}

          <div>
            <label className="label">Notes</label>
            <input className="input" placeholder="Any special instructions..." value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} />
          </div>

          <div className="flex gap-3">
            <button className="btn-secondary flex-1" onClick={() => setShowModal(false)}>Cancel</button>
            <button className="btn-primary flex-1" onClick={handleCreate} disabled={saving}>
              {saving ? 'Creating...' : 'Create Order'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
