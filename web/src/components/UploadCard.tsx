import React from 'react'

type Props = {
  onFileSelected: (file: File) => void
  uploading: boolean
  fileLabel?: string
  pageInfo?: string
}

export default function UploadCard({ onFileSelected, uploading, fileLabel, pageInfo }: Props) {
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onFileSelected(file)
  }
  return (
    <div className="bg-white rounded-2xl shadow p-6 border">
      <div className="mb-4 text-lg font-semibold">PDF Reader</div>
      <div className="border-2 border-dashed rounded-xl p-10 text-center">
        <div className="mx-auto w-12 h-12 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-12 h-12 text-gray-400">
            <path d="M6 2a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8.828a2 2 0 00-.586-1.414l-4.828-4.828A2 2 0 0013.172 2H6z"/>
            <path d="M14 2v4a2 2 0 002 2h4"/>
          </svg>
        </div>
        <div className="text-2xl font-bold mb-1">Upload PDF</div>
        <div className="text-sm text-gray-500 mb-4">(Accept only PDF. Max size: 10 MB)</div>
        <label className="inline-flex items-center px-4 py-2 rounded-lg bg-gray-900 text-white cursor-pointer hover:opacity-90">
          <input type="file" accept="application/pdf" className="hidden" onChange={onChange} />
          {uploading ? 'Uploading...' : 'Choose File'}
        </label>
        {fileLabel && (
          <div className="mt-4 text-sm font-medium text-gray-700">{fileLabel} <span className="text-green-600">✓</span></div>
        )}
        {pageInfo && <div className="text-xs text-gray-500 mt-1">{pageInfo}</div>}
      </div>
    </div>
  )
}
