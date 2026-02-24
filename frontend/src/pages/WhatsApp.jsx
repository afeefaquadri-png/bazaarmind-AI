import { useState, useRef, useEffect } from 'react'
import { useShop } from '../hooks/useShop.jsx'
import { waApi, productApi } from '../services/api.js'
import { Send, MessageSquare, Bot, User, Zap, RefreshCw } from 'lucide-react'

function ChatBubble({ message, isBot, timestamp }) {
  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-3`}>
      <div className={`chat-bubble ${isBot ? 'incoming' : 'outgoing'}`}>
        {isBot && <div className="flex items-center gap-1.5 mb-1"><Bot size={12} className="text-emerald-600" /><span className="text-xs font-semibold text-emerald-700">BazaarMind Bot</span></div>}
        <p className="whitespace-pre-line text-sm">{message}</p>
        <p className="text-[10px] text-right mt-1 text-surface-400">{timestamp}</p>
      </div>
    </div>
  )
}

const EXAMPLE_MESSAGES = [
  '2 milk 1 bread',
  'Teen doodh do bag',
  '5 biscuits 2 chips',
  '1 shirt size L color black',
  'two eggs one bread one butter',
]

export default function WhatsApp() {
  const { currentShop } = useShop()
  const [messages, setMessages] = useState([
    { text: `👋 Welcome to *${currentShop?.name || 'BazaarMind'}*!\n\nSend your order and I'll parse it with AI.\nExample: "2 milk 1 bread"`, isBot: true, ts: now() }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [parseResult, setParseResult] = useState(null)
  const [products, setProducts] = useState([])
  const bottomRef = useRef(null)

  function now() {
    return new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (!currentShop?.id) return
    productApi.list(currentShop.id).then(({ data }) => setProducts(data)).catch(console.error)
    setMessages([{
      text: `👋 Welcome to *${currentShop?.name}*!\n\nSend your order and I'll parse it with AI.\nExample: "2 milk 1 bread"`,
      isBot: true, ts: now()
    }])
    setParseResult(null)
  }, [currentShop?.id])

  const sendMessage = async (msg = input) => {
    if (!msg.trim() || !currentShop?.id) return
    const userMsg = msg.trim()
    setInput('')

    setMessages(p => [...p, { text: userMsg, isBot: false, ts: now() }])
    setLoading(true)

    try {
      const { data } = await waApi.simulate({
        shop_id: currentShop.id,
        customer_phone: '9999999999',
        message: userMsg,
        customer_name: 'Demo Customer',
      })

      setParseResult(data.parsed)
      setMessages(p => [...p, { text: data.reply_preview, isBot: true, ts: now() }])
    } catch (e) {
      setMessages(p => [...p, {
        text: '⚠️ Error processing order. Make sure the backend is running.',
        isBot: true, ts: now()
      }])
    }
    setLoading(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (!currentShop) {
    return (
      <div className="h-full flex items-center justify-center text-surface-400 p-8 text-center">
        <div>
          <MessageSquare size={40} strokeWidth={1.5} className="mx-auto mb-3" />
          <p>Please select a shop to test the WhatsApp bot.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 animate-fade-in">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-surface-900">WhatsApp Bot Simulator</h1>
        <p className="text-surface-500 text-sm mt-0.5">Test AI order parsing without a real WhatsApp number</p>
      </div>

      <div className="grid grid-cols-5 gap-4 h-[calc(100vh-180px)]">
        {/* Chat Window */}
        <div className="col-span-3 flex flex-col bg-white rounded-2xl border border-surface-200 overflow-hidden shadow-sm">
          {/* Chat Header */}
          <div className="bg-[#075e54] px-4 py-3 flex items-center gap-3 flex-shrink-0">
            <div className="w-9 h-9 bg-emerald-400 rounded-full flex items-center justify-center">
              <MessageSquare size={16} className="text-white" />
            </div>
            <div>
              <p className="text-white font-semibold text-sm">{currentShop.name}</p>
              <p className="text-emerald-300 text-xs flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse-dot inline-block" />
                BazaarMind AI Bot Active
              </p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 bg-[#efeae2]" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4c9bc' fill-opacity='0.2'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")" }}>
            {messages.map((msg, i) => (
              <ChatBubble key={i} message={msg.text} isBot={msg.isBot} timestamp={msg.ts} />
            ))}
            {loading && (
              <div className="flex justify-start mb-3">
                <div className="chat-bubble incoming">
                  <div className="flex gap-1">
                    {[0, 1, 2].map(i => (
                      <div key={i} className="w-2 h-2 bg-surface-400 rounded-full animate-bounce" style={{ animationDelay: `${i*0.15}s` }} />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="bg-[#f0f2f5] px-3 py-2.5 flex items-center gap-2 flex-shrink-0">
            <input
              className="flex-1 bg-white rounded-full px-4 py-2 text-sm focus:outline-none"
              placeholder="Type an order: 2 milk 1 bread..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="w-9 h-9 bg-[#075e54] rounded-full flex items-center justify-center text-white disabled:opacity-50 hover:bg-[#054d44] transition-colors"
            >
              <Send size={15} />
            </button>
          </div>
        </div>

        {/* Right Panel */}
        <div className="col-span-2 space-y-4 overflow-y-auto">
          {/* Quick Examples */}
          <div className="card">
            <h3 className="font-semibold text-surface-800 mb-3 flex items-center gap-2">
              <Zap size={15} className="text-amber-500" /> Quick Test Messages
            </h3>
            <div className="space-y-2">
              {EXAMPLE_MESSAGES.map((msg, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(msg)}
                  className="w-full text-left text-sm px-3 py-2 rounded-lg border border-surface-200 hover:bg-brand-50 hover:border-brand-300 transition-colors text-surface-700 font-mono"
                  disabled={loading}
                >
                  "{msg}"
                </button>
              ))}
            </div>
          </div>

          {/* Parse Result */}
          {parseResult && (
            <div className="card">
              <h3 className="font-semibold text-surface-800 mb-3 flex items-center gap-2">
                <Bot size={15} className="text-brand-600" /> AI Parse Result
                <span className="badge badge-blue ml-auto">{parseResult.parse_method}</span>
              </h3>
              <p className="text-xs text-surface-500 mb-3 font-mono">"{parseResult.raw_message}"</p>
              <div className="space-y-2">
                {parseResult.items?.map((item, i) => (
                  <div key={i} className={`p-3 rounded-xl border ${item.matched_product_id ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'}`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-semibold text-surface-800">{item.name}</p>
                        {item.matched_product_name && (
                          <p className="text-xs text-emerald-700 mt-0.5">✅ Matched: {item.matched_product_name}</p>
                        )}
                        {!item.matched_product_id && (
                          <p className="text-xs text-red-600 mt-0.5">❌ No match found</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold">×{item.quantity}</p>
                        {item.unit_price && <p className="text-xs text-surface-500">₹{item.unit_price}</p>}
                      </div>
                    </div>
                    <div className="mt-1.5 h-1 bg-surface-200 rounded-full">
                      <div
                        className={`h-1 rounded-full ${item.confidence >= 0.8 ? 'bg-emerald-500' : item.confidence >= 0.5 ? 'bg-amber-500' : 'bg-red-500'}`}
                        style={{ width: `${(item.confidence || 0) * 100}%` }}
                      />
                    </div>
                    <p className="text-xs text-surface-400 mt-0.5">Confidence: {Math.round((item.confidence || 0) * 100)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Product List */}
          <div className="card">
            <h3 className="font-semibold text-surface-800 mb-3">Available Products ({products.length})</h3>
            <div className="space-y-1.5 max-h-56 overflow-y-auto">
              {products.length === 0 ? (
                <p className="text-sm text-surface-400 text-center py-4">No products. Add some in Products page first!</p>
              ) : (
                products.map(p => (
                  <div key={p.id} className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-surface-50">
                    <span className="text-sm font-medium text-surface-700">{p.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-surface-400">₹{p.price}</span>
                      <span className={`badge text-xs ${p.stock > p.low_stock_alert ? 'badge-green' : 'badge-red'}`}>
                        {p.stock} {p.unit}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
