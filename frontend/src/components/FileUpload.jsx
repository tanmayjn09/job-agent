import { useRef, useState } from 'react'

export default function FileUpload({ onFile, accept = '.pdf,.doc,.docx,.txt', multiple = false, label = 'Upload file', sublabel = '' }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const [files, setFiles] = useState([])

  const handleFiles = (newFiles) => {
    const fileList = Array.from(newFiles)
    setFiles(multiple ? [...files, ...fileList] : fileList)
    onFile(multiple ? [...files, ...fileList] : fileList[0])
  }

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files) }}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
        dragging ? 'border-brand-500 bg-brand-50' :
        files.length ? 'border-green-400 bg-green-50' :
        'border-gray-200 hover:border-brand-300 hover:bg-gray-50'
      }`}
    >
      <input ref={inputRef} type="file" accept={accept} multiple={multiple} className="hidden"
        onChange={(e) => handleFiles(e.target.files)} />

      {files.length === 0 ? (
        <div>
          <div className="text-3xl mb-2">📄</div>
          <p className="font-medium text-gray-700">{label}</p>
          {sublabel && <p className="text-sm text-gray-400 mt-1">{sublabel}</p>}
          <p className="text-xs text-gray-400 mt-3">Drag and drop or click to browse</p>
        </div>
      ) : (
        <div>
          <div className="text-2xl mb-2">✅</div>
          {files.map((f, i) => (
            <p key={i} className="text-sm font-medium text-green-700">{f.name}</p>
          ))}
          <p className="text-xs text-gray-400 mt-2">Click to replace</p>
        </div>
      )}
    </div>
  )
}
