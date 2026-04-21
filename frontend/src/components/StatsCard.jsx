export const StatsCard = ({ label, value, icon, bgColor = 'from-blue-600 to-blue-700' }) => {
  return (
    <div className={`bg-gradient-to-br ${bgColor} rounded-xl p-6 text-white border border-slate-700`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-300 text-sm font-medium">{label}</p>
          <p className="text-4xl font-bold text-white mt-2">{value}</p>
        </div>
        <div className="text-5xl opacity-80">{icon}</div>
      </div>
    </div>
  );
};
