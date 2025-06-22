'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Settings, Key, Sparkles, MessageCircle } from 'lucide-react'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [developerMessage, setDeveloperMessage] = useState('You are a helpful AI assistant.')
  const [apiKey, setApiKey] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || !apiKey.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date()
    }

    // Create a placeholder for the assistant's response
    const assistantMessageId = (Date.now() + 1).toString();
    const placeholderMessage: Message = {
      id: assistantMessageId,
      content: '', // This will be filled by the stream or an error
      role: 'assistant',
      timestamp: new Date()
    };
    
    const messageToSend = inputMessage;
    // Add both user message and placeholder to the state, and clear the input
    setMessages(prev => [...prev, userMessage, placeholderMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          developer_message: developerMessage,
          user_message: messageToSend,
          model: 'gpt-4.1-mini',
          api_key: apiKey
        })
      })

      if (!response.ok) {
        // Try to get a specific error message from the backend
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `The server responded with status ${response.status}.`);
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('Could not get a reader from the response body.');

      let assistantMessageContent = ''
      let messageReceived = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        assistantMessageContent += chunk
        if(chunk.trim().length > 0) {
            messageReceived = true
        }

        // Update the assistant message in real-time
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessageId 
              ? { ...msg, content: assistantMessageContent }
              : msg
          )
        )
      }

      if (!messageReceived) {
        throw new Error('The API returned an empty response. This may be due to an invalid API key or lack of credits.');
      }
    } catch (error: any) {
      console.error('Error during chat:', error);
      // Update the placeholder with a helpful error message
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: `⚠️ **An error occurred.**\n\nPlease check your API key and network connection.\n\n*Details: ${error.message}*` }
            : msg
        )
      );
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="chat-container">
        {/* Header */}
        <header className="chat-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 tracking-tight">AI Chat</h1>
                <p className="text-sm text-gray-500 font-medium">Powered by GPT-4.1-mini</p>
              </div>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-2xl transition-all duration-200 group"
            >
              <Settings className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
            </button>
          </div>
        </header>

        {/* Settings Panel */}
        {showSettings && (
          <div className="settings-panel">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <Key className="w-4 h-4 mr-2 text-blue-500" />
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="settings-input"
                />
                <p className="text-xs text-gray-500 mt-2">Your API key is never stored on our servers</p>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  System Message
                </label>
                <textarea
                  value={developerMessage}
                  onChange={(e) => setDeveloperMessage(e.target.value)}
                  placeholder="You are a helpful AI assistant."
                  rows={3}
                  className="settings-textarea"
                />
                <p className="text-xs text-gray-500 mt-2">Customize how the AI behaves</p>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="welcome-container">
              <div className="welcome-icon">
                <MessageCircle className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3 tracking-tight">Welcome to AI Chat</h3>
              <p className="text-gray-600 max-w-md mx-auto leading-relaxed">
                Start a conversation with AI. Set your API key in the settings to begin chatting.
              </p>
            </div>
          )}
          
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`chat-message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}>
                <div className="flex items-start space-x-3">
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    <p className="message-time">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                      <User className="w-4 h-4 text-blue-500" />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="chat-message assistant-message">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot" style={{ animationDelay: '0.1s' }}></div>
                    <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
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
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type a message..."
              disabled={isLoading || !apiKey.trim()}
              className="message-input"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim() || !apiKey.trim()}
              className="send-button"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          
          {!apiKey.trim() && (
            <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-2xl">
              <p className="text-sm text-amber-700 font-medium">
                ⚠️ Please set your OpenAI API key in the settings to start chatting.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 