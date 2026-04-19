import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useLeads, useDashboardStats } from '../hooks/useLeads';
import { UploadZone } from '../components/UploadZone';
import { LeadsTable } from '../components/LeadsTable';
import { StatsCard } from '../components/StatsCard';

export default function Dashboard() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { leads, loading, refetch } = useLeads();
  const { stats } = useDashboardStats();
  const [selectedScoreFilter, setSelectedScoreFilter] = useState(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleLeadSelect = (lead) => {
    navigate(`/leads/${lead.id}`);
  };

  const handleUploadSuccess = (data) => {
    setTimeout(() => refetch(), 1000);
  };

  // Get recently uploaded leads (last 10)
  const recentLeads = [...leads]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 10);

  // Get scored leads (hot + warm)
  const scoredLeads = leads.filter(lead => lead.score === 'hot' || lead.score === 'warm');

  // Get hot leads (ready for sales)
  const hotLeads = leads.filter(lead => lead.score === 'hot');

  const scoreGroups = [
    { score: 'hot', label: 'Hot Leads', icon: '🔴', color: 'red', count: stats?.by_score?.hot || 0 },
    { score: 'warm', label: 'Warm Leads', icon: '🟡', color: 'amber', count: stats?.by_score?.warm || 0 },
    { score: 'cold', label: 'Cold Leads', icon: '⚪', color: 'gray', count: stats?.by_score?.cold || 0 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center text-white font-bold">
              WL
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">Lead Gen Pro</h1>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition font-medium"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10">

        {/* SECTION 1: UPLOAD LEADS */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-8 mb-10">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 text-xl">
              📤
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Upload Leads</h2>
            <span className="ml-auto text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
              {stats?.total || 0} total leads
            </span>
          </div>
          <UploadZone onSuccess={handleUploadSuccess} />
        </div>

        {/* SECTION 2: LEAD SCORING SELECTOR */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 text-xl">
              ⭐
            </div>
            Lead Scoring
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {scoreGroups.map((group) => (
              <button
                key={group.score}
                onClick={() => setSelectedScoreFilter(selectedScoreFilter === group.score ? null : group.score)}
                className={`p-6 rounded-xl border-2 transition-all cursor-pointer ${
                  selectedScoreFilter === group.score
                    ? `border-${group.color}-500 bg-${group.color}-50 shadow-lg`
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md'
                }`}
              >
                <div className="text-4xl mb-3">{group.icon}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{group.label}</h3>
                <p className={`text-3xl font-bold ${
                  group.score === 'hot' ? 'text-red-600' :
                  group.score === 'warm' ? 'text-amber-600' :
                  'text-gray-600'
                }`}>
                  {group.count}
                </p>
                <p className="text-sm text-gray-500 mt-2">Click to filter</p>
              </button>
            ))}
          </div>
        </div>

        {/* SECTION 3: RECENTLY UPLOADED & SCORED LEADS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recently Uploaded Leads */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-transparent">
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-3">
                  <span className="text-2xl">📋</span>
                  Recently Uploaded Leads
                </h3>
                <p className="text-sm text-gray-500 mt-1">{recentLeads.length} recent leads</p>
              </div>

              <div className="overflow-x-auto">
                {recentLeads.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <p className="text-lg">No leads yet</p>
                    <p className="text-sm">Upload a file to get started</p>
                  </div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Phone</th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Score</th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentLeads.map((lead) => (
                        <tr
                          key={lead.id}
                          onClick={() => handleLeadSelect(lead)}
                          className="border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition"
                        >
                          <td className="px-6 py-4 font-medium text-gray-900">
                            {lead.first_name} {lead.last_name}
                          </td>
                          <td className="px-6 py-4 text-gray-600">{lead.phone}</td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                              lead.score === 'hot' ? 'bg-red-100 text-red-700' :
                              lead.score === 'warm' ? 'bg-amber-100 text-amber-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {lead.score === 'hot' ? '🔴 Hot' :
                               lead.score === 'warm' ? '🟡 Warm' :
                               '⚪ Cold'}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                              {lead.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>

          {/* Leads Handed Over to Sales Guy */}
          <div>
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-md border border-green-200 overflow-hidden h-full flex flex-col">
              <div className="p-6 border-b border-green-200 bg-gradient-to-r from-green-100 to-emerald-100">
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-3">
                  <span className="text-2xl">🎯</span>
                  Sales Ready
                </h3>
                <p className="text-sm text-gray-600 mt-1">Leads qualified for sales team</p>
              </div>

              <div className="flex-1 overflow-y-auto p-4">
                {hotLeads.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-center">
                    <div>
                      <p className="text-5xl mb-3">🤝</p>
                      <p className="text-gray-600 font-medium">No hot leads yet</p>
                      <p className="text-sm text-gray-500 mt-2">Leads will appear here once qualified</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {hotLeads.map((lead) => (
                      <div
                        key={lead.id}
                        onClick={() => handleLeadSelect(lead)}
                        className="bg-white p-4 rounded-lg border-2 border-green-200 hover:border-green-400 hover:shadow-md cursor-pointer transition"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-bold text-gray-900">{lead.first_name} {lead.last_name}</p>
                            <p className="text-sm text-gray-600">{lead.phone}</p>
                          </div>
                          <span className="text-2xl">🔴</span>
                        </div>
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <span className="text-xs font-bold text-green-700 bg-green-100 px-2 py-1 rounded-full">
                            Ready for Sales
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="p-4 bg-green-100 border-t border-green-200">
                <p className="text-sm font-bold text-green-800">
                  {hotLeads.length} lead{hotLeads.length !== 1 ? 's' : ''} qualified
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
