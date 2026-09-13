export default function Pagination({ meta, onPageChange }) {
  if (!meta || meta.total <= meta.page_size) return null

  const totalPages = Math.ceil(meta.total / meta.page_size)
  const currentPage = meta.page

  return (
    <div className="flex items-center justify-between mt-4">
      <span className="text-sm text-gray-500">
        Showing {(currentPage - 1) * meta.page_size + 1}-
        {Math.min(currentPage * meta.page_size, meta.total)} of {meta.total}
      </span>
      <div className="flex gap-1">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          Prev
        </button>
        {Array.from({ length: totalPages }, (_, i) => i + 1)
          .filter((p) => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 2)
          .map((p, idx, arr) => (
            <span key={p} className="flex items-center">
              {idx > 0 && arr[idx - 1] !== p - 1 && (
                <span className="px-1 text-gray-400">...</span>
              )}
              <button
                onClick={() => onPageChange(p)}
                className={`px-3 py-1 text-sm border rounded ${
                  p === currentPage
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'hover:bg-gray-50'
                }`}
              >
                {p}
              </button>
            </span>
          ))}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          Next
        </button>
      </div>
    </div>
  )
}
