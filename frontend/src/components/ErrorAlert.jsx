export default function ErrorAlert({ error }) {
  if (!error) return null

  const data = error.response?.data
  const message = data?.error?.message || data?.detail || error.message || 'Something went wrong'
  const code = data?.error?.code
  const requestId = data?.request_id

  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
      <div className="flex items-start gap-3">
        <span className="text-red-500 text-lg">&#9888;</span>
        <div>
          <p className="text-red-800 font-medium">{message}</p>
          {code && (
            <p className="text-red-600 text-sm mt-1">Error code: {code}</p>
          )}
          {requestId && (
            <p className="text-red-400 text-xs mt-1">Request ID: {requestId}</p>
          )}
        </div>
      </div>
    </div>
  )
}
