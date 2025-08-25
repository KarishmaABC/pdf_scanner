import React from 'react'
import axios from 'axios'
import UploadCard from './components/UploadCard'
import ChatBox from './components/ChatBox'
import type { Message } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function App() {
  const [docId, setDocId] = React.useState<string | null>(null)
  const [fileLabel, setFileLabel] = React.useState<string | undefined>(undefined)
  const [pageInfo, setPageInfo] = React.useState<string | undefined>(undefined)
  const [uploading, setUploading] = React.useState(false)
  const [messages, setMessages] = React.useState<Message[]>([])
  const [thinking, setThinking] = React.useState(false)

  const onFileSelected = async (file: File) => {
    if (file.type !== 'application/pdf') {
      alert('Please select a PDF file.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      alert('Max size is 10 MB for this demo.')
      return
    }
    setUploading(true)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await axios.post(`${API_URL}/api/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const data = res.data
      setDocId(data.doc_id)
      setFileLabel(`PDF: ${file.name}`)
      setPageInfo(`Pages: ${data.page_count}  Uploaded successfully`)
    } catch (e: any) {
      console.error(e)
      alert(e?.response?.data?.detail ?? 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const ask = async (q: string) => {
    if (!docId) { alert('Upload a PDF first.'); return }
    const next: Message[] = [...messages, { role: 'user', content: q }]
    setMessages(next)
    setThinking(true)
    try {
      const res = await axios.post(`${API_URL}/api/chat`, {
        doc_id: docId, question: q, history: messages
      })
      const ans = res.data.answer as string
      setMessages([...next, { role: 'assistant', content: ans }])
    } catch (e: any) {
      console.error(e)
      setMessages([...next, { role: 'assistant', content: 'Sorry — something went wrong.' }])
    } finally {
      setThinking(false)
    }
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <UploadCard onFileSelected={onFileSelected} uploading={uploading} fileLabel={fileLabel} pageInfo={pageInfo} />
        <ChatBox messages={messages} onSend={ask} disabled={!docId || uploading} thinking={thinking} />
      </div>
    </div>
  )
}
