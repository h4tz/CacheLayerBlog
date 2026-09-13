import { useRail } from '../context/RailContext'

export default function RailToggle() {
  const { rail, switchRail } = useRail()

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-gray-500">API Rail:</span>
      <button
        onClick={() => switchRail('drf')}
        className={`px-3 py-1 rounded-l-md font-medium transition ${
          rail === 'drf'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        DRF
      </button>
      <button
        onClick={() => switchRail('ninja')}
        className={`px-3 py-1 rounded-r-md font-medium transition ${
          rail === 'ninja'
            ? 'bg-purple-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        Ninja
      </button>
    </div>
  )
}
