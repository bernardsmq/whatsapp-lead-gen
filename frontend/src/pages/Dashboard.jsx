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
  const [selectedLead, setSelectedLead] = useState(null);

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

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">WhatsApp Lead Gen</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatsCard
            title="Hot Leads"
            value={stats?.by_score?.hot || 0}
            icon="🔴"
            color="red"
          />
          <StatsCard
            title="Warm Leads"
            value={stats?.by_score?.warm || 0}
            icon="🟡"
            color="amber"
          />
          <StatsCard
            title="Cold Leads"
            value={stats?.by_score?.cold || 0}
            icon="⚪"
            color="gray"
          />
          <StatsCard
            title="Total Leads"
            value={stats?.total || 0}
            icon="👥"
            color="blue"
          />
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg border p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Leads</h2>
          <UploadZone onSuccess={handleUploadSuccess} />
        </div>

        {/* Leads Table */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">All Leads</h2>
          <LeadsTable
            leads={leads}
            loading={loading}
            onSelectLead={handleLeadSelect}
          />
        </div>
      </main>
    </div>
  );
}
