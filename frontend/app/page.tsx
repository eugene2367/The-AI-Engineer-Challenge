'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Settings, Key, Sparkles, MessageCircle, Info, Cpu, X, Clipboard } from 'lucide-react'
import FileUpload from './components/FileUpload'
import type React from 'react'

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

  const lastAssistantIdx = messages.map((m: Message, i: number) => m.role === 'assistant' ? i : -1).filter((i: number) => i !== -1).pop()

  return (
    <div className="min-h-screen flex flex-col bloomberg-grid">
      {/* Bloomberg Terminal Header */}
      <header className="bloomberg-header flex items-center justify-between sticky top-0 z-40">
        <span>Bloomberg AI Terminal</span>
        <span className="text-xs font-mono">Financial Document Q&A</span>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="ml-4 p-2 rounded-full bg-yellow-400 text-black hover:bg-yellow-300 border border-yellow-400 transition flex items-center justify-center"
          title="Settings"
          style={{ position: 'relative', zIndex: 50 }}
        >
          <Settings className="w-6 h-6" />
        </button>
      </header>
      {/* Settings Panel */}
      {showSettings && (
        <div className="settings-panel flex flex-col gap-4 border-b-2 border-yellow-400 bg-[#181c1c] p-6 font-mono">
          <label className="text-yellow-300 font-bold text-sm">OpenAI API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="settings-input bg-black/80 border-yellow-400 text-yellow-200 font-mono rounded px-4 py-2"
            autoComplete="off"
          />
          <span className="text-xs text-yellow-400">Your key is stored locally in your browser and never sent to our server.</span>
        </div>
      )}
      {/* Welcome/Instructions for Financial Analysts */}
      {messages.length === 0 && (
        <div className="welcome-container">
          <div className="welcome-icon">💹</div>
          <h2 className="text-2xl font-bold mb-2">Welcome to the Bloomberg AI Terminal</h2>
          <p className="mb-4">Upload earnings reports, financial statements, or analyst PDFs and ask questions about them. Get instant, AI-powered answers tailored for financial analysis.</p>
          <p className="text-yellow-400">Supported: PDF, DOCX, TXT (max 4.5MB)</p>
        </div>
      )}
      {/* File Upload */}
      <div className="my-4">
        <FileUpload onFileProcessed={handleFileProcessed} disabled={!apiKey.trim()} />
      </div>
      {/* Chat Area */}
      <div className="flex-1 overflow-hidden px-4 py-2">
        <div
          className="chat-scroll-area h-full max-h-[60vh] overflow-y-auto pr-2"
          style={{ scrollbarGutter: 'stable' }}
          ref={messagesEndRef}
        >
          {messages.map((msg, idx) => (
            <div
              key={msg.id}
              className={`chat-message ${msg.role === 'user' ? 'user-message' : 'assistant-message'} my-2 relative`}
            >
              <div className="flex items-center justify-between">
                <span>{msg.content}</span>
                <span className="message-time">{msg.timestamp.toLocaleTimeString()}</span>
              </div>
              {/* Copy button for last assistant message */}
              {msg.role === 'assistant' && idx === lastAssistantIdx && (
                <button
                  className="absolute bottom-2 right-2 px-2 py-1 bg-black/80 border border-yellow-400 text-yellow-300 rounded font-mono text-xs flex items-center gap-1 hover:bg-yellow-400 hover:text-black transition"
                  title="Copy to clipboard"
                  onClick={() => {
                    navigator.clipboard.writeText(msg.content)
                  }}
                >
                  <Clipboard className="w-4 h-4 mr-1" /> Copy
                </button>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
      {/* Input Area */}
      <form onSubmit={handleSubmit} className="input-container flex items-center space-x-2">
        <input
          className="message-input flex-1"
          type="text"
          placeholder="Ask a question about your uploaded document..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isLoading || !currentDocumentId || !apiKey.trim()}
        />
        <button
          className="send-button"
          type="submit"
          disabled={isLoading || !currentDocumentId || !apiKey.trim()}
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
      {/* API Key Warning */}
      {!apiKey.trim() && (
        <div className="mt-2 p-2 bg-yellow-900 text-yellow-300 rounded font-mono text-xs">
          Please enter your OpenAI API key in Settings to use the app.
        </div>
      )}
      {/* Error Display */}
      {error && (
        <div className="mt-2 p-2 bg-red-900 text-red-400 rounded font-mono text-xs">{error}</div>
      )}
      {/* Bloomberg Terminal Footer */}
      <footer className="bloomberg-footer">
        &copy; {new Date().getFullYear()} Bloomberg AI Terminal &mdash; For Financial Analysts
      </footer>
    </div>
  )
}