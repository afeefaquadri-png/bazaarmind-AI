import { useState, useEffect } from 'react'
import { useShop } from '../hooks/useShop.jsx'
import { productApi } from '../services/api.js'
import Modal from '../components/Modal.jsx'
import DynamicProductForm, { validateAttributes } from '../components/DynamicProductForm.jsx'
import { Plus, Search, Edit, Trash2, AlertTriangle, Package } from 'lucide-react'

export default function Products() {
  const { currentShop } = useShop()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: '', price: '', stock: '', unit: 'piece', attributes: {}, description: '' })
  const [attrErrors, setAttrErrors] = useState({})
  const [saving, setSaving] = useState(false)
  const [filterLowStock, setFilterLowStock] = useState(false)

  const template = currentShop?.template || {}
  const units = template.units || ['piece']

  const load = async () => {
    if (!currentShop?.id) { setLoading(false); return }
    setLoading(true)
    try {
      const { data } = await productApi.list(currentShop.id)
      setProducts(data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  useEffect(() => { load() }, [currentShop?.id])

  const openCreate = () => {
    setEditing(null)
    setForm({ name: '', price: '', stock: '', unit: units[0] || 'piece', attributes: {}, description: '' })
    setAttrErrors({})
    setShowModal(true)
  }

  const openEdit = (product) => {
    setEditing(product)
    setForm({
      name: product.name,
      price: product.price,
      stock: product.stock,
      unit: product.unit,
      attributes: product.attributes || {},
      description: product.description || '',
    })
    setAttrErrors({})
    setShowModal(true)
  }

  const handleSave = async () => {
    const errors = validateAttributes(form.attributes, template)
    if (!form.name || !form.price || form.stock === '') {
      alert('Name, price, and stock are required')
      return
    }
    if (Object.keys(errors).length > 0) {
      setAttrErrors(errors)
      return
    }
    setSaving(true)
    try {
      const payload = {
        ...form,
        price: parseFloat(form.price),
        stock: parseInt(form.stock),
        shop_id: currentShop.id,
      }
      if (editing) {
        await productApi.update(editing.id, payload)
      } else {
        await productApi.create(payload)
      }
      setShowModal(false)
      load()
    } catch (e) { alert(e.response?.data?.detail || 'Save failed') }
    setSaving(false)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this product?')) return
    await productApi.delete(id)
    load()
  }

  const filtered = products.filter(p => {
    const match = p.name.toLowerCase().includes(search.toLowerCase())
    if (filterLowStock) return match && p.stock <= p.low_stock_alert
    return match
  })

  const lowStockCount = products.filter(p => p.stock <= p.low_stock_alert).length

  if (!currentShop) {
    return (
      <div className="h-full flex items-center justify-center text-surface-400">
        <p>Please select or create a shop first.</p>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900">Products</h1>
          <p className="text-surface-500 text-sm mt-0.5">{template?.icon} {template?.label}</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={openCreate}>
          <Plus size={16} /> Add Product
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400" />
          <input
            type="text"
            className="input pl-9"
            placeholder="Search products..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <button
          onClick={() => setFilterLowStock(p => !p)}
          className={`flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-sm font-medium border transition-colors
            ${filterLowStock ? 'bg-red-50 border-red-200 text-red-700' : 'bg-white border-surface-200 text-surface-600 hover:bg-surface-50'}`}
        >
          <AlertTriangle size={14} />
          Low Stock {lowStockCount > 0 && <span className="badge badge-red">{lowStockCount}</span>}
        </button>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-3">
            {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-12 rounded-xl" />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-surface-400 gap-3">
            <Package size={40} strokeWidth={1.5} />
            <p className="text-sm">{search ? 'No products match your search' : 'No products yet. Add your first product!'}</p>
            {!search && <button className="btn-primary text-sm" onClick={openCreate}>+ Add Product</button>}
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-surface-50 border-b border-surface-100">
              <tr>
                <th className="table-header">Product</th>
                <th className="table-header">Stock</th>
                <th className="table-header">Price</th>
                <th className="table-header">Unit</th>
                <th className="table-header">Attributes</th>
                <th className="table-header w-24">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(product => (
                <tr key={product.id} className="table-row">
                  <td className="table-cell font-medium text-surface-900">{product.name}</td>
                  <td className="table-cell">
                    <span className={`font-mono font-semibold ${product.stock <= product.low_stock_alert ? 'text-red-600' : 'text-emerald-600'}`}>
                      {product.stock}
                    </span>
                    {product.stock <= product.low_stock_alert && (
                      <span className="ml-2 badge badge-red">Low</span>
                    )}
                  </td>
                  <td className="table-cell font-semibold">₹{product.price}</td>
                  <td className="table-cell text-surface-500">{product.unit}</td>
                  <td className="table-cell">
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(product.attributes || {}).map(([k, v]) => (
                        <span key={k} className="badge badge-gray">{k}: {v}</span>
                      ))}
                    </div>
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center gap-1">
                      <button onClick={() => openEdit(product)} className="p-1.5 rounded-lg hover:bg-surface-100 text-surface-500 hover:text-brand-600 transition-colors">
                        <Edit size={14} />
                      </button>
                      <button onClick={() => handleDelete(product.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-surface-500 hover:text-red-600 transition-colors">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Product Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editing ? 'Edit Product' : 'Add Product'} size="lg">
        <div className="space-y-4">
          {/* Core Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="label">Product Name <span className="text-red-500">*</span></label>
              <input className="input" placeholder="e.g. Amul Milk 500ml" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
            </div>
            <div>
              <label className="label">Price (₹) <span className="text-red-500">*</span></label>
              <input type="number" className="input" placeholder="0.00" value={form.price} onChange={e => setForm(p => ({ ...p, price: e.target.value }))} />
            </div>
            <div>
              <label className="label">Stock Quantity <span className="text-red-500">*</span></label>
              <input type="number" className="input" placeholder="0" value={form.stock} onChange={e => setForm(p => ({ ...p, stock: e.target.value }))} />
            </div>
            <div>
              <label className="label">Unit</label>
              <select className="input" value={form.unit} onChange={e => setForm(p => ({ ...p, unit: e.target.value }))}>
                {units.map(u => <option key={u} value={u}>{u}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Description</label>
              <input className="input" placeholder="Optional description" value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} />
            </div>
          </div>

          {/* Dynamic Attributes */}
          {template?.attributes?.length > 0 && (
            <div className="border-t border-surface-100 pt-4">
              <DynamicProductForm
                template={template}
                value={form.attributes}
                onChange={attrs => setForm(p => ({ ...p, attributes: attrs }))}
                errors={attrErrors}
              />
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button className="btn-secondary flex-1" onClick={() => setShowModal(false)}>Cancel</button>
            <button className="btn-primary flex-1" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : (editing ? 'Update Product' : 'Add Product')}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
