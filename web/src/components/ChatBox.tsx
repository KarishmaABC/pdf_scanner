import React, { useRef, useEffect } from 'react'
import type { Message } from '../types'

type Props = {
  messages: Message[]
  onSend: (text: string) => void
  disabled?: boolean
  thinking?: boolean
}

export default function ChatBox({ messages, onSend, disabled, thinking }: Props) {
  const [text, setText] = React.useState('')
  const endRef = useRef<HTMLDivElement | null>(null)
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, thinking])

  return (
    <div className="bg-white rounded-2xl shadow p-6 border">
      <div className="space-y-3 max-h-[460px] overflow-y-auto pr-2">
        {messages.length === 0 && (
          <div className="text-gray-500 text-sm">Ask questions about your PDF, e.g. “What are the payment terms in this contract?”</div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`${m.role === 'user' ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'} rounded-2xl px-4 py-2 max-w-[80%] whitespace-pre-wrap`}>
              {m.content}
            </div>
          </div>
        ))}
        {thinking && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 rounded-2xl px-4 py-2 max-w-[80%]">Thinking…</div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div className="mt-4 flex gap-2">
        <input
          className="flex-1 border rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-gray-300"
          placeholder="Ask a question…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && text.trim()) { onSend(text.trim()); setText('') } }}
          disabled={disabled}
        />
        <button
          onClick={() => { if (text.trim()) { onSend(text.trim()); setText('') } }}
          className="px-4 py-2 rounded-xl bg-gray-900 text-white disabled:opacity-50"
          disabled={disabled}
        >
          Send
        </button>
      </div>
    </div>
  )
}
