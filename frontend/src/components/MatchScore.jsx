export default function MatchScore({ score }) {
  const color = score >= 75 ? 'text-green-600' : score >= 50 ? 'text-yellow-600' : 'text-red-500'
  const bg = score >= 75 ? 'bg-green-100' : score >= 50 ? 'bg-yellow-100' : 'bg-red-100'
  const bar = score >= 75 ? 'bg-green-500' : score >= 50 ? 'bg-yellow-500' : 'bg-red-400'
  const label = score >= 75 ? 'Strong match' : score >= 50 ? 'Good match' : 'Partial match'

  return (
    <div className={`${bg} rounded-lg px-3 py-2 min-w-[90px]`}>
      <div className={`text-xl font-bold ${color}`}>{Math.round(score)}%</div>
      <div className="w-full h-1 bg-white/60 rounded-full mt-1">
        <div className={`h-1 rounded-full ${bar}`} style={{ width: `${score}%` }} />
      </div>
      <div className={`text-xs mt-1 ${color} font-medium`}>{label}</div>
    </div>
  )
}
