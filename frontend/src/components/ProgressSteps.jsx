export default function ProgressSteps({ steps, current }) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((step, i) => (
        <div key={i} className="flex items-center">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
            i < current ? 'bg-brand-500 text-white' :
            i === current ? 'bg-brand-50 text-brand-600 border border-brand-500' :
            'bg-gray-100 text-gray-400'
          }`}>
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
              i < current ? 'bg-white text-brand-500' :
              i === current ? 'bg-brand-500 text-white' :
              'bg-gray-300 text-white'
            }`}>
              {i < current ? '✓' : i + 1}
            </span>
            {step}
          </div>
          {i < steps.length - 1 && (
            <div className={`w-8 h-0.5 ${i < current ? 'bg-brand-500' : 'bg-gray-200'}`} />
          )}
        </div>
      ))}
    </div>
  )
}
