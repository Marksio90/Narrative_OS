'use client'

import { useState, useRef, useEffect } from 'react'
import {
  Sparkles,
  X,
  Send,
  Loader2,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  FileText,
  Users,
  MessageSquare,
  Wand2,
  RefreshCw,
  Minimize2,
  Maximize2,
} from 'lucide-react'

interface AICopilotProps {
  projectId: number
  accessToken: string
  onClose: () => void
  selectedText?: string
  currentChapter?: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

type PromptTemplate = {
  id: string
  label: string
  icon: any
  prompt: string
  requiresSelection: boolean
}

export default function AICopilot({
  projectId,
  accessToken,
  onClose,
  selectedText = '',
  currentChapter,
}: AICopilotProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [isMinimized, setIsMinimized] = useState(false)
  const [showTemplates, setShowTemplates] = useState(true)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const promptTemplates: PromptTemplate[] = [
    {
      id: 'continue',
      label: 'Kontynuuj tekst',
      icon: FileText,
      prompt: `Kontynuuj następujący fragment tekstu w tym samym stylu:\n\n${selectedText}`,
      requiresSelection: true,
    },
    {
      id: 'rephrase',
      label: 'Przeformułuj',
      icon: RefreshCw,
      prompt: `Przeformułuj poniższy fragment, zachowując znaczenie ale zmieniając styl:\n\n${selectedText}`,
      requiresSelection: true,
    },
    {
      id: 'expand',
      label: 'Rozwiń',
      icon: Wand2,
      prompt: `Rozwiń poniższy fragment, dodając więcej szczegółów i opisów:\n\n${selectedText}`,
      requiresSelection: true,
    },
    {
      id: 'dialogue',
      label: 'Zasugeruj dialog',
      icon: MessageSquare,
      prompt: 'Zasugeruj naturalny dialog pasujący do tej sceny',
      requiresSelection: false,
    },
    {
      id: 'character',
      label: 'Pomysł na postać',
      icon: Users,
      prompt: 'Zasugeruj interesującą postać dla mojej historii',
      requiresSelection: false,
    },
    {
      id: 'idea',
      label: 'Pomysł fabularny',
      icon: Lightbulb,
      prompt: 'Zasugeruj interesujący zwrot akcji lub pomysł fabularny',
      requiresSelection: false,
    },
  ]

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (selectedText && messages.length === 0) {
      setShowTemplates(true)
    }
  }, [selectedText])

  const handleSend = async (customPrompt?: string) => {
    const messageText = customPrompt || input.trim()

    if (!messageText || loading) return

    const userMessage: Message = {
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    }

    setMessages([...messages, userMessage])
    setInput('')
    setLoading(true)
    setShowTemplates(false)

    try {
      // Call AI generation endpoint
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/ai/draft`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            prompt: messageText,
            chapter_number: currentChapter,
            mode: 'copilot',
            max_length: 500,
          }),
        }
      )

      if (response.ok) {
        const data = await response.json()

        const assistantMessage: Message = {
          role: 'assistant',
          content: data.content || 'Przepraszam, nie udało mi się wygenerować odpowiedzi.',
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])
      } else {
        const assistantMessage: Message = {
          role: 'assistant',
          content: 'Przepraszam, wystąpił błąd. Spróbuj ponownie.',
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (error) {
      console.error('AI Copilot error:', error)
      const assistantMessage: Message = {
        role: 'assistant',
        content: 'Przepraszam, wystąpił błąd połączenia.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleTemplateClick = (template: PromptTemplate) => {
    if (template.requiresSelection && !selectedText) {
      alert('Najpierw zaznacz fragment tekstu w edytorze')
      return
    }

    handleSend(template.prompt)
  }

  const handleCopy = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedIndex(index)
      setTimeout(() => setCopiedIndex(null), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div
      className={`fixed right-6 bottom-6 bg-gray-800 border border-gray-700 rounded-2xl shadow-2xl transition-all duration-300 ${
        isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'
      } flex flex-col overflow-hidden`}
      style={{ zIndex: 1000 }}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-white bg-opacity-20 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-bold text-sm">AI Copilot</h3>
            <p className="text-purple-100 text-xs">Twój asystent pisarza</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
          >
            {isMinimized ? (
              <Maximize2 className="w-4 h-4 text-white" />
            ) : (
              <Minimize2 className="w-4 h-4 text-white" />
            )}
          </button>
          <button
            onClick={onClose}
            className="p-1 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
          >
            <X className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <Sparkles className="w-12 h-12 text-purple-400 mx-auto mb-3 animate-pulse" />
                <p className="text-gray-400 text-sm mb-2">Witaj! Jestem AI Copilot</p>
                <p className="text-gray-500 text-xs">Zaznacz tekst lub wybierz szablon poniżej</p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-800 text-gray-200 border border-gray-700'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                  <div className="flex items-center justify-between mt-2 gap-2">
                    <span className="text-xs opacity-60">
                      {message.timestamp.toLocaleTimeString('pl-PL', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>

                    {message.role === 'assistant' && (
                      <button
                        onClick={() => handleCopy(message.content, index)}
                        className="p-1 hover:bg-gray-700 rounded transition-colors"
                      >
                        {copiedIndex === index ? (
                          <Check className="w-3 h-3 text-green-400" />
                        ) : (
                          <Copy className="w-3 h-3 opacity-60 hover:opacity-100" />
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3">
                  <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Prompt Templates */}
          {showTemplates && messages.length === 0 && (
            <div className="bg-gray-800 border-t border-gray-700 p-3">
              <button
                onClick={() => setShowTemplates(!showTemplates)}
                className="w-full flex items-center justify-between text-sm text-gray-400 hover:text-gray-300 mb-2"
              >
                <span>Szablony</span>
                {showTemplates ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronUp className="w-4 h-4" />
                )}
              </button>

              <div className="grid grid-cols-2 gap-2">
                {promptTemplates.map((template) => {
                  const Icon = template.icon
                  const isDisabled = template.requiresSelection && !selectedText

                  return (
                    <button
                      key={template.id}
                      onClick={() => handleTemplateClick(template)}
                      disabled={isDisabled}
                      className={`flex items-center gap-2 p-2 rounded-lg text-xs transition-colors ${
                        isDisabled
                          ? 'bg-gray-700 text-gray-500 cursor-not-allowed opacity-50'
                          : 'bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white'
                      }`}
                    >
                      <Icon className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{template.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="bg-gray-800 border-t border-gray-700 p-3">
            <div className="flex items-end gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  selectedText
                    ? 'Zaznaczono tekst - wybierz szablon lub wpisz własne polecenie...'
                    : 'Wpisz polecenie dla AI...'
                }
                rows={2}
                className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
              />

              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
                className="p-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex-shrink-0"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-2">
              Enter = wyślij • Shift+Enter = nowa linia
            </p>
          </div>
        </>
      )}
    </div>
  )
}
