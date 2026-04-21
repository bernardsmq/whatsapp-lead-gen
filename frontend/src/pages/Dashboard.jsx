import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useLeads, useDashboardStats } from '../hooks/useLeads';
import { UploadZone } from '../components/UploadZone';
import { ManualLeadForm } from '../components/ManualLeadForm';
import { StatsCard } from '../components/StatsCard';
import Sidebar from '../components/Sidebar';
import { analyticsAPI } from '../lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { leads, loading, refetch } = useLeads();
  const { stats } = useDashboardStats();
  const [recentActivity, setRecentActivity] = useState([]);
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    const fetchActivity = async () => {
      try {
        const response = await analyticsAPI.getRecentActivity(15);
        setRecentActivity(response.data);
      } catch (error) {
        console.error('Failed to fetch activity', error);
      }
    };
    fetchActivity();
    const interval = setInterval(fetchActivity, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleLeadSelect = (lead) => {
    navigate(`/leads/${lead.id}`);
  };

  const handleUploadSuccess = () => {
    setTimeout(() => refetch(), 1000);
  };

  const handleManualLeadAdded = () => {
    setTimeout(() => refetch(), 500);
  };

  const hotLeads = leads.filter(lead => lead.score === 'hot');
  const warmLeads = leads.filter(lead => lead.score === 'warm');
  const aiMessagesSent = (stats?.by_status?.qualified || 0) + (stats?.by_status?.sent_to_sales || 0);
  const conversionRate = stats?.total > 0 ? Math.round((hotLeads.length / stats?.total) * 100) : 0;

  if (currentPage !== 'dashboard') {
    return (
      <div className="flex min-h-screen bg-slate-900">
        <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} onLogout={handleLogout} />
        <main className="flex-1 ml-64 bg-slate-900 p-8">
          {currentPage === 'import' && (
            <div className="max-w-4xl mx-auto">
              <h1 className="text-3xl font-bold text-white mb-8">Import Leads</h1>
              <div className="bg-slate-800 rounded-xl p-8 border border-slate-700">
                <UploadZone onSuccess={handleUploadSuccess} />
                <div className="mt-8 pt-8 border-t border-slate-700">
                  <ManualLeadForm onSuccess={handleManualLeadAdded} />
                </div>
              </div>
            </div>
          )}
          {currentPage === 'all-leads' && <AllLeadsPage leads={leads} onSelectLead={handleLeadSelect} />}
          {currentPage === 'hot-leads' && <FilteredLeadsPage leads={hotLeads} filter="hot" onSelectLead={handleLeadSelect} />}
          {currentPage === 'warm-leads' && <FilteredLeadsPage leads={warmLeads} filter="warm" onSelectLead={handleLeadSelect} />}
          {currentPage === 'analytics' && <AnalyticsPage stats={stats} />}
          {currentPage === 'messages' && <MessagesPage />}
          {currentPage === 'settings' && <SettingsPage />}
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-900">
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} onLogout={handleLogout} />

      <main className="flex-1 ml-64">
        {/* Header */}
        <header className="sticky top-0 z-40 bg-slate-800 border-b border-slate-700 px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Dashboard</h1>
              <p className="text-slate-400 mt-1">Welcome back to RCR AI Lead Gen</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-slate-400 hover:text-slate-200 transition"
            >
              Logout
            </button>
          </div>
        </header>

        <div className="p-8">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <StatsCard
              label="Total Leads"
              value={stats?.total || 0}
              icon="📊"
              bgColor="from-blue-600 to-blue-700"
            />
            <StatsCard
              label="Hot Leads"
              value={hotLeads.length}
              icon="🔴"
              bgColor="from-red-600 to-red-700"
            />
            <StatsCard
              label="AI Messages Sent"
              value={aiMessagesSent}
              icon="💬"
              bgColor="from-purple-600 to-purple-700"
            />
            <StatsCard
              label="Conversion Rate"
              value={`${conversionRate}%`}
              icon="📈"
              bgColor="from-green-600 to-green-700"
            />
          </div>

          {/* Live Activity Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
            <div className="lg:col-span-2 bg-slate-800 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-2xl">⚡</span> Live Activity
              </h2>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {recentActivity.length === 0 ? (
                  <p className="text-slate-400 text-center py-8">No recent activity</p>
                ) : (
                  recentActivity.map((activity, idx) => (
                    <div key={idx} className="bg-slate-700 p-4 rounded-lg border border-slate-600 hover:border-yellow-500 transition">
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">{activity.icon}</span>
                        <div className="flex-1">
                          <p className="font-semibold text-white">{activity.title}</p>
                          <p className="text-sm text-slate-400">{activity.description}</p>
                          <p className="text-xs text-slate-500 mt-1">
                            {new Date(activity.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Pipeline Summary */}
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="text-2xl">📊</span> Pipeline
              </h2>
              <div className="space-y-3">
                <div className="bg-slate-700 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-300 font-medium">Hot Leads</span>
                    <span className="bg-red-600 text-white px-3 py-1 rounded-full font-bold text-sm">
                      {hotLeads.length}
                    </span>
                  </div>
                  <div className="w-full bg-slate-600 rounded-full h-2">
                    <div
                      className="bg-red-600 h-2 rounded-full transition-all"
                      style={{ width: stats?.total > 0 ? `${(hotLeads.length / stats.total) * 100}%` : '0%' }}
                    />
                  </div>
                </div>

                <div className="bg-slate-700 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-300 font-medium">Warm Leads</span>
                    <span className="bg-yellow-600 text-white px-3 py-1 rounded-full font-bold text-sm">
                      {warmLeads.length}
                    </span>
                  </div>
                  <div className="w-full bg-slate-600 rounded-full h-2">
                    <div
                      className="bg-yellow-600 h-2 rounded-full transition-all"
                      style={{ width: stats?.total > 0 ? `${(warmLeads.length / stats.total) * 100}%` : '0%' }}
                    />
                  </div>
                </div>

                <div className="bg-slate-700 p-4 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-300 font-medium">Cold Leads</span>
                    <span className="bg-slate-500 text-white px-3 py-1 rounded-full font-bold text-sm">
                      {stats?.by_score?.cold || 0}
                    </span>
                  </div>
                  <div className="w-full bg-slate-600 rounded-full h-2">
                    <div
                      className="bg-slate-500 h-2 rounded-full transition-all"
                      style={{ width: stats?.total > 0 ? `${((stats?.by_score?.cold || 0) / stats.total) * 100}%` : '0%' }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function AllLeadsPage({ leads, onSelectLead }) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      <div className="bg-slate-700 px-6 py-4 border-b border-slate-600">
        <h2 className="text-xl font-bold text-white">All Leads</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-700 border-b border-slate-600">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">LEAD</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">PHONE</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">INTEREST</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">SCORE</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">LAST CONTACT</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">STATUS</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">ACTION</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id} className="border-b border-slate-700 hover:bg-slate-700 transition">
                <td className="px-6 py-4 text-white font-medium">{lead.first_name} {lead.last_name}</td>
                <td className="px-6 py-4 text-slate-300">{lead.phone}</td>
                <td className="px-6 py-4 text-slate-400">Car Rental</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    lead.score === 'hot' ? 'bg-red-600 text-white' :
                    lead.score === 'warm' ? 'bg-yellow-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {lead.score === 'hot' ? '🔴' : lead.score === 'warm' ? '🟡' : '⚪'} {lead.score}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-400">
                  {new Date(lead.updated_at || lead.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-slate-700 text-slate-300 rounded text-xs font-medium">
                    {lead.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => onSelectLead(lead)}
                    className="text-yellow-400 hover:text-yellow-300 font-medium transition"
                  >
                    View Chat
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FilteredLeadsPage({ leads, filter, onSelectLead }) {
  const filterLabels = {
    hot: 'Hot Leads',
    warm: 'Warm Leads',
    cold: 'Cold Leads'
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      <div className="bg-slate-700 px-6 py-4 border-b border-slate-600">
        <h2 className="text-xl font-bold text-white">{filterLabels[filter]}</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-700 border-b border-slate-600">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">LEAD</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">PHONE</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">SCORE</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">STATUS</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">ACTION</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id} className="border-b border-slate-700 hover:bg-slate-700 transition">
                <td className="px-6 py-4 text-white font-medium">{lead.first_name} {lead.last_name}</td>
                <td className="px-6 py-4 text-slate-300">{lead.phone}</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    lead.score === 'hot' ? 'bg-red-600 text-white' :
                    lead.score === 'warm' ? 'bg-yellow-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {lead.score === 'hot' ? '🔴' : lead.score === 'warm' ? '🟡' : '⚪'} {lead.score}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-slate-700 text-slate-300 rounded text-xs font-medium">
                    {lead.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => onSelectLead(lead)}
                    className="text-yellow-400 hover:text-yellow-300 font-medium transition"
                  >
                    View Chat
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AnalyticsPage({ stats }) {
  return (
    <div className="max-w-6xl">
      <h1 className="text-3xl font-bold text-white mb-8">Analytics</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <p className="text-slate-400 text-sm font-medium mb-2">Qualification Rate</p>
          <p className="text-4xl font-bold text-white">{stats?.qualification_rate || 0}%</p>
          <p className="text-slate-500 text-xs mt-2">Leads with all details</p>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <p className="text-slate-400 text-sm font-medium mb-2">Reply Rate</p>
          <p className="text-4xl font-bold text-white">{stats?.reply_rate || 0}%</p>
          <p className="text-slate-500 text-xs mt-2">Leads that responded</p>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <p className="text-slate-400 text-sm font-medium mb-2">Avg Lead Score</p>
          <p className="text-4xl font-bold text-white">{stats?.avg_score || 0}</p>
          <p className="text-slate-500 text-xs mt-2">Hot=3, Warm=2, Cold=1</p>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <p className="text-slate-400 text-sm font-medium mb-2">Sales Handoffs Today</p>
          <p className="text-4xl font-bold text-white">{stats?.sales_handoffs_today || 0}</p>
          <p className="text-slate-500 text-xs mt-2">Sent to sales team</p>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <p className="text-slate-400 text-sm font-medium mb-2">Total Sales Handoffs</p>
          <p className="text-4xl font-bold text-white">{stats?.total_sales_handoffs || 0}</p>
          <p className="text-slate-500 text-xs mt-2">All time</p>
        </div>

        <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
          <p className="text-slate-400 text-sm font-medium mb-2">Full Info Gathered</p>
          <p className="text-4xl font-bold text-white">{stats?.full_info_gathered || 0}%</p>
          <p className="text-slate-500 text-xs mt-2">Complete lead data</p>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <h2 className="text-xl font-bold text-white mb-6">AI Performance</h2>
        <div className="space-y-6">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-slate-300">Reply Rate</span>
              <span className="text-white font-bold">{stats?.reply_rate || 0}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${stats?.reply_rate || 0}%` }} />
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <span className="text-slate-300">Full Info Gathered</span>
              <span className="text-white font-bold">{stats?.full_info_gathered || 0}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${stats?.full_info_gathered || 0}%` }} />
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <span className="text-slate-300">Qualification Rate</span>
              <span className="text-white font-bold">{stats?.qualification_rate || 0}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${stats?.qualification_rate || 0}%` }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MessagesPage() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchMessages = async () => {
      setLoading(true);
      try {
        const response = await analyticsAPI.getMessagesByDate(selectedDate);
        setMessages(response.data);
      } catch (error) {
        console.error('Failed to fetch messages', error);
      }
      setLoading(false);
    };
    fetchMessages();
  }, [selectedDate]);

  return (
    <div className="max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Messages Sent</h1>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
        />
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="bg-slate-700 px-6 py-4 border-b border-slate-600">
          <p className="text-slate-300">
            Showing {messages.length} message{messages.length !== 1 ? 's' : ''} for {selectedDate}
          </p>
        </div>
        <div className="divide-y divide-slate-700">
          {loading ? (
            <p className="px-6 py-8 text-center text-slate-400">Loading messages...</p>
          ) : messages.length === 0 ? (
            <p className="px-6 py-8 text-center text-slate-400">No messages for this date</p>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className="px-6 py-4 hover:bg-slate-700 transition cursor-pointer">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-semibold text-white">{msg.lead_name}</p>
                    <p className="text-sm text-slate-400">{msg.lead_phone}</p>
                    <p className="text-slate-300 mt-2">{msg.message}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      msg.sender === 'ai' ? 'bg-yellow-600 text-white' : 'bg-slate-600 text-slate-300'
                    }`}>
                      {msg.sender === 'ai' ? '🤖 Sent' : '📩 Received'}
                    </span>
                    <p className="text-xs text-slate-500 mt-2">✓ {msg.delivery_status}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function SettingsPage() {
  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold text-white mb-8">Settings</h1>
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 text-center">
        <p className="text-slate-400">Settings coming soon...</p>
      </div>
    </div>
  );
}
