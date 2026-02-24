import { useState, useEffect } from 'react'
import { useShop } from '../hooks/useShop.jsx'
import { shopApi } from '../services/api.js'
import Modal from '../components/Modal.jsx'
import { Plus, Store, Trash2, Check } from 'lucide-react'

const CATEGORIES = {
  retail:       { label: 'Retail',          color: 'bg-blue-100 text-blue-700' },
  fashion:      { label: 'Fashion',         color: 'bg-pink-100 text-pink-700' },
  automotive:   { label: 'Automotive',      color: 'bg-orange-100 text-orange-700' },
  food:         { label: 'Food & Beverage', color: 'bg-green-100 text-green-700' },
  health:       { label: 'Health & Pharma', color: 'bg-red-100 text-red-700' },
  home:         { label: 'Home & Hardware', color: 'bg-amber-100 text-amber-700' },
  electronics:  { label: 'Electronics',     color: 'bg-purple-100 text-purple-700' },
  others:       { label: 'Others',          color: 'bg-gray-100 text-gray-700' },
}

export default function Shops() {
  const { shops, currentShop, selectShop, addShop, removeShop, refresh } = useShop()
  const [showCreate, setShowCreate] = useState(false)
  const [shopTypes, setShopTypes] = useState({ types: [], categories: {} })
  const [selectedType, setSelectedType] = useState('')
  const [form, setForm] = useState({ name: '', phone: '', owner_name: '', address: '', city: '', email: '', whatsapp_number: '' })
  const [saving, setSaving] = useState(false)
  const [catFilter, setCatFilter] = useState('all')

  useEffect(() => {
    shopApi.types().then(({ data }) => setShopTypes(data)).catch(console.error)
  }, [])

  const handleCreate = async () => {
    if (!form.name || !form.phone || !selectedType) {
      alert('Shop name, phone, and type are required')
      return
    }
    setSaving(true)
    try {
      const { data } = await shopApi.create({ ...form, shop_type: selectedType })
      addShop(data)
      setShowCreate(false)
      setForm({ name: '', phone: '', owner_name: '', address: '', city: '', email: '', whatsapp_number: '' })
      setSelectedType('')
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to create shop')
    }
    setSaving(false)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this shop and all its data?')) return
    await shopApi.delete(id)
    removeShop(id)
    refresh()
  }

  const filteredTypes = catFilter === 'all'
    ? shopTypes.types
    : shopTypes.types.filter(t => t.category === catFilter)

  return (
    <div className="p-6 space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900">Shops</h1>
          <p className="text-surface-500 text-sm mt-0.5">Manage all your shop profiles</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowCreate(true)}>
          <Plus size={16} /> Create Shop
        </button>
      </div>

      {/* Shop Cards */}
      {shops.length === 0 ? (
        <div className="card flex flex-col items-center py-16 gap-4 text-center">
          <Store size={48} strokeWidth={1.5} className="text-surface-300" />
          <h2 className="text-lg font-bold text-surface-700">No shops yet</h2>
          <p className="text-surface-400 text-sm max-w-xs">Create your first shop to start managing inventory, orders, and AI-powered insights.</p>
          <button className="btn-primary" onClick={() => setShowCreate(true)}>Create Your First Shop</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {shops.map(shop => (
            <div
              key={shop.id}
              onClick={() => selectShop(shop)}
              className={`card cursor-pointer hover:shadow-md transition-all hover:-translate-y-0.5 relative ${currentShop?.id === shop.id ? 'ring-2 ring-brand-500' : ''}`}
            >
              {currentShop?.id === shop.id && (
                <div className="absolute top-3 right-3 w-6 h-6 bg-brand-600 rounded-full flex items-center justify-center">
                  <Check size={12} className="text-white" />
                </div>
              )}
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 bg-surface-50 border border-surface-200 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">
                  {shop.template?.icon || '🏪'}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-surface-900 truncate">{shop.name}</h3>
                  <p className="text-sm text-surface-500">{shop.template?.label}</p>
                  {shop.owner_name && <p className="text-xs text-surface-400 mt-0.5">Owner: {shop.owner_name}</p>}
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <div className="space-y-0.5">
                  <p className="text-xs text-surface-400">{shop.phone}</p>
                  {shop.city && <p className="text-xs text-surface-400">{shop.city}</p>}
                </div>
                <button
                  onClick={e => { e.stopPropagation(); handleDelete(shop.id) }}
                  className="p-1.5 rounded-lg text-surface-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Shop Modal */}
      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Create New Shop" size="xl">
        <div className="space-y-5">
          {/* Step 1: Shop Type */}
          <div>
            <h3 className="font-semibold text-surface-800 mb-3">1. Select Shop Type</h3>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2 mb-3">
              {['all', ...Object.keys(CATEGORIES)].map(cat => (
                <button
                  key={cat}
                  onClick={() => setCatFilter(cat)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors border
                    ${catFilter === cat ? 'bg-brand-600 text-white border-brand-600' : 'bg-white border-surface-200 text-surface-600 hover:bg-surface-50'}`}
                >
                  {cat === 'all' ? 'All Types' : CATEGORIES[cat]?.label || cat}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-52 overflow-y-auto pr-1">
              {filteredTypes.map(type => (
                <button
                  key={type.type}
                  onClick={() => setSelectedType(type.type)}
                  className={`p-3 rounded-xl border-2 text-left transition-all
                    ${selectedType === type.type
                      ? 'border-brand-500 bg-brand-50'
                      : 'border-surface-200 bg-white hover:border-surface-300 hover:bg-surface-50'}`}
                >
                  <div className="text-xl mb-1">{type.icon}</div>
                  <p className="text-xs font-medium text-surface-800 leading-tight">{type.label}</p>
                </button>
              ))}
            </div>

            {selectedType && (
              <div className="mt-2 flex items-center gap-2 text-brand-700 text-sm font-medium">
                <Check size={14} /> Selected: {shopTypes.types.find(t => t.type === selectedType)?.label}
              </div>
            )}
          </div>

          {/* Step 2: Shop Details */}
          <div className="border-t border-surface-100 pt-4">
            <h3 className="font-semibold text-surface-800 mb-3">2. Shop Details</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="label">Shop Name <span className="text-red-500">*</span></label>
                <input className="input" placeholder="e.g. Ramesh Kirana Store" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
              </div>
              <div>
                <label className="label">Owner Name</label>
                <input className="input" placeholder="Full name" value={form.owner_name} onChange={e => setForm(p => ({ ...p, owner_name: e.target.value }))} />
              </div>
              <div>
                <label className="label">Phone Number <span className="text-red-500">*</span></label>
                <input className="input" placeholder="9999999999" value={form.phone} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))} />
              </div>
              <div>
                <label className="label">WhatsApp Number</label>
                <input className="input" placeholder="WhatsApp (if different)" value={form.whatsapp_number} onChange={e => setForm(p => ({ ...p, whatsapp_number: e.target.value }))} />
              </div>
              <div>
                <label className="label">City</label>
                <input className="input" placeholder="Mumbai, Delhi..." value={form.city} onChange={e => setForm(p => ({ ...p, city: e.target.value }))} />
              </div>
              <div className="col-span-2">
                <label className="label">Address</label>
                <input className="input" placeholder="Shop address" value={form.address} onChange={e => setForm(p => ({ ...p, address: e.target.value }))} />
              </div>
              <div className="col-span-2">
                <label className="label">Email</label>
                <input type="email" className="input" placeholder="shop@example.com" value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} />
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button className="btn-secondary flex-1" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary flex-1" onClick={handleCreate} disabled={saving || !selectedType}>
              {saving ? 'Creating...' : 'Create Shop'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
