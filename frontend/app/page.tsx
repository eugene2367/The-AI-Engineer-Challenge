'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Settings, Key, Sparkles, MessageCircle, Info, Cpu, X } from 'lucide-react'
import FileUpload from './components/FileUpload'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [developerMessage, setDeveloperMessage] = useState('You are a helpful AI assistant operating in a futuristic, high-tech interface.')
  const [apiKey, setApiKey] = useState('')
  const [projectId, setProjectId] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [currentDocumentId, setCurrentDocumentId] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (apiKey) {
      localStorage.setItem('openai_api_key', apiKey);
    }
  }, [apiKey]);

  const handleFileProcessed = (success: boolean, docId?: string) => {
    console.log('File processed:', { success, docId })
    if (success && docId) {
      setCurrentDocumentId(docId)
      setError(null)
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: 'Document uploaded successfully! You can now ask questions about its contents.',
        role: 'assistant',
        timestamp: new Date()
      }])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!currentDocumentId) {
      setError('Please upload a document first')
      return
    }
    if (!query.trim()) {
      setError('Please enter a question')
      return
    }

    setIsLoading(true)
    setError(null)
    setResponse('')

    // Add user message to chat
    const userMessage = {
      id: Date.now().toString() + '-user',
      content: query,
      role: 'user' as const,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: currentDocumentId,
          query,
          api_key: apiKey,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to query document' }))
        throw new Error(errorData.detail || `Query failed with status ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Failed to get response reader')
      }

      let aiContent = ''
      // Read the stream
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // Convert the chunk to text
        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n')

        // Process each line
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              break
            }
            try {
              const parsed = JSON.parse(data)
              if (parsed.error) {
                throw new Error(parsed.error)
              }
              if (parsed.token) {
                aiContent += parsed.token
                // Update the last assistant message or add a new one
                setMessages((prev) => {
                  // If the last message is assistant, update it
                  if (prev.length > 0 && prev[prev.length - 1].role === 'assistant') {
                    const updated = [...prev]
                    updated[updated.length - 1] = {
                      ...updated[updated.length - 1],
                      content: aiContent,
                    }
                    return updated
                  } else {
                    // Otherwise, add a new assistant message
                    return [
                      ...prev,
                      {
                        id: Date.now().toString() + '-ai',
                        content: aiContent,
                        role: 'assistant' as const,
                        timestamp: new Date(),
                      },
                    ]
                  }
                })
              }
            } catch (e) {
              console.error('Error parsing chunk:', e)
              if (e instanceof Error) {
                setError(e.message)
              }
            }
          }
        }
      }
    } catch (err) {
      console.error('Error querying document:', err)
      setError(err instanceof Error ? err.message : 'Failed to query document')
    } finally {
      setIsLoading(false)
      setQuery('')
      scrollToBottom()
    }
  }

  return (
    <div className="min-h-screen">
      <div className="chat-container">
        {/* Header */}
        <header className="chat-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600/80 to-slate-800/80 rounded-2xl flex items-center justify-center shadow-lg border border-slate-700">
                <Cpu className="w-6 h-6 text-blue-300 animate-pulse" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-100 tracking-tight">AI Mainframe</h1>
                <p className="text-sm text-blue-400 font-medium">ONLINE</p>
              </div>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-3 text-slate-400 hover:text-blue-400 hover:bg-slate-800/50 rounded-2xl transition-all duration-200 group"
            >
              <Settings className={`w-5 h-5 transition-transform duration-500 ${showSettings ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </header>

        {/* Settings Panel */}
        {showSettings && (
          <div className="settings-panel">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-slate-200">System Configuration</h2>
              <button onClick={() => setShowSettings(false)} className="p-2 text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-3 flex items-center">
                  <Key className="w-4 h-4 mr-2 text-blue-400" />
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-proj-..."
                  className="settings-input"
                />
              </div>
               <div>
                <label className="block text-sm font-semibold text-slate-300 mb-3 flex items-center">
                  <Info className="w-4 h-4 mr-2 text-blue-400" />
                  OpenAI Project ID
                </label>
                <input
                  type="text"
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  placeholder="proj_..."
                  className="settings-input"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-3">
                  System Directive
                </label>
                <textarea
                  value={developerMessage}
                  onChange={(e) => setDeveloperMessage(e.target.value)}
                  placeholder="You are a helpful AI assistant."
                  rows={3}
                  className="settings-textarea"
                />
              </div>
            </div>
          </div>
        )}

        {/* File Upload */}
        <FileUpload onFileProcessed={handleFileProcessed} />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4" style={{ maxHeight: '60vh' }}>
          {messages.length === 0 && (
            <div className="welcome-container">
              <div className="welcome-icon">
                <Sparkles className="w-10 h-10 text-blue-400" />
              </div>
              <h3 className="text-2xl font-semibold text-slate-100 mb-3 tracking-tight">AI Mainframe Initialized</h3>
              <p className="text-slate-400 max-w-md mx-auto leading-relaxed">
                System online. Awaiting input. Configure API credentials in the settings panel.
              </p>
            </div>
          )}
          {messages.map((message, idx) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`chat-message ${
                  message.role === 'user'
                    ? 'user-message bg-blue-600 text-white ml-auto'
                    : 'assistant-message bg-slate-800 text-slate-200'
                }`}
                style={{ maxWidth: '80%' }}
              >
                <div className="flex items-start space-x-3">
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600/80 to-slate-800/80 rounded-full flex items-center justify-center flex-shrink-0 mt-1 border border-slate-700">
                      <Bot className="w-4 h-4 text-blue-300" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    <p className="message-time">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-slate-800/80 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm border border-slate-700">
                      <User className="w-4 h-4 text-blue-300" />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="chat-message assistant-message bg-slate-800 text-slate-200">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-slate-800 rounded-full flex items-center justify-center flex-shrink-0 mt-1 border-slate-700">
                    <Bot className="w-4 h-4 text-blue-300" />
                  </div>
                  <div className="typing-indicator">
                    <div className="typing-dot" style={{ animationDelay: '0.1s' }}></div>
                    <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
                    <div className="typing-dot" style={{ animationDelay: '0.3s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="input-container">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your question here..."
              disabled={isLoading || !apiKey.trim()}
              className="message-input"
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim() || !apiKey.trim()}
              className="send-button"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          
          {!apiKey.trim() && (
            <div className="mt-3 p-3 bg-amber-900/50 border border-amber-500/30 rounded-2xl">
              <p className="text-sm text-amber-300 font-medium flex items-center">
                <Info size={16} className="mr-2 flex-shrink-0" />
                SYSTEM OFFLINE: API credentials required for connection.
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
} 