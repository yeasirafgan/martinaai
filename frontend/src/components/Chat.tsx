'use client'
import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import InputBar from './InputBar'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Conversation {
  id: string
  title: string
  messages: Message[]
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'

export default function Chat() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [streamMode, setStreamMode] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  const activeConversation = conversations.find(c => c.id === activeId) ?? null
  const messages = activeConversation?.messages ?? []

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const updateMessages = (id: string, updater: (prev: Message[]) => Message[]) => {
    setConversations(prev =>
      prev.map(c => c.id === id ? { ...c, messages: updater(c.messages) } : c)
    )
  }

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMsg: Message = { role: 'user', content: text }

    let conversationId = activeId
    if (!conversationId) {
      conversationId = crypto.randomUUID()
      const newConv: Conversation = {
        id: conversationId,
        title: text.slice(0, 40),
        messages: [],
      }
      setConversations(prev => [newConv, ...prev])
      setActiveId(conversationId)
    }

    const currentId = conversationId
    const history = [...messages, userMsg]

    setConversations(prev =>
      prev.map(c =>
        c.id === currentId
          ? { ...c, messages: [...history, { role: 'assistant', content: '' }] }
          : c
      )
    )
    setIsLoading(true)

    try {
      if (streamMode) {
        const res = await fetch(`${API_URL}/conversation/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: history, max_tokens: 1024 }),
        })

        if (!res.ok || !res.body) throw new Error('API error')

        const reader = res.body.getReader()
        const decoder = new TextDecoder()

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          const chunk = decoder.decode(value)
          updateMessages(currentId, prev => {
            const updated = [...prev]
            updated[updated.length - 1] = {
              role: 'assistant',
              content: updated[updated.length - 1].content + chunk,
            }
            return updated
          })
        }
      } else {
        const res = await fetch(`${API_URL}/conversation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: history, max_tokens: 1024 }),
        })

        if (!res.ok) throw new Error('API error')
        const data = await res.json()
        updateMessages(currentId, prev => {
          const updated = [...prev]
          updated[updated.length - 1] = { role: 'assistant', content: data.reply }
          return updated
        })
      }
    } catch {
      updateMessages(currentId, prev => {
        const updated = [...prev]
        updated[updated.length - 1] = {
          role: 'assistant',
          content: 'Something went wrong. Please try again.',
        }
        return updated
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-gray-200 flex flex-col p-5 shrink-0">
        <h1 className="text-lg font-bold text-gray-900 tracking-tight mb-6">Martinaai</h1>

        <button
          onClick={() => setActiveId(null)}
          className="w-full text-left text-sm px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors mb-3"
        >
          + New chat
        </button>

        <div className="flex-1 overflow-y-auto space-y-0.5 min-h-0">
          {conversations.map(conv => (
            <div
              key={conv.id}
              className={`group flex items-center rounded-lg transition-colors ${
                conv.id === activeId ? 'bg-purple-50' : 'hover:bg-gray-100'
              }`}
            >
              <button
                onClick={() => setActiveId(conv.id)}
                className={`flex-1 text-left text-sm px-3 py-2 truncate ${
                  conv.id === activeId ? 'text-purple-700 font-medium' : 'text-gray-600'
                }`}
              >
                {conv.title}
              </button>
              <button
                onClick={() => {
                  setConversations(prev => prev.filter(c => c.id !== conv.id))
                  if (activeId === conv.id) setActiveId(null)
                }}
                className="opacity-0 group-hover:opacity-100 pr-2 text-gray-400 hover:text-red-500 transition-all shrink-0"
              >
                ×
              </button>
            </div>
          ))}
        </div>

        <div className="border-t border-gray-100 pt-4 mt-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Response mode</p>
          <div className="flex rounded-lg border border-gray-200 overflow-hidden text-xs">
            <button
              onClick={() => setStreamMode(true)}
              className={`flex-1 py-1.5 transition-colors ${
                streamMode ? 'bg-purple-600 text-white' : 'text-gray-500 hover:bg-gray-50'
              }`}
            >
              Stream
            </button>
            <button
              onClick={() => setStreamMode(false)}
              className={`flex-1 py-1.5 transition-colors ${
                !streamMode ? 'bg-purple-600 text-white' : 'text-gray-500 hover:bg-gray-50'
              }`}
            >
              Instant
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-12 h-12 rounded-2xl bg-purple-600 flex items-center justify-center text-white text-xl font-bold mb-4">
                M
              </div>
              <h2 className="text-xl font-semibold text-gray-700">How can I help you today?</h2>
              <p className="text-gray-400 mt-2 text-sm">Ask me anything — I remember the conversation.</p>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map((msg, i) => (
                <MessageBubble
                  key={i}
                  message={msg}
                  isStreaming={streamMode && isLoading && i === messages.length - 1}
                />
              ))}
              {!streamMode && isLoading && (
                <div className="flex items-end gap-2 justify-start">
                  <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                    AI
                  </div>
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm">
                    <span className="flex gap-1">
                      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
                    </span>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <InputBar onSend={sendMessage} disabled={isLoading} />
      </main>
    </div>
  )
}
