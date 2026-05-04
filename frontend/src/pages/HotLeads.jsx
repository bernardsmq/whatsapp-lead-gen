import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { leadsAPI } from '../lib/api';
import { formatInDubaiTz } from '../lib/dateUtils';

export default function HotLeads() {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await leadsAPI.getAll(null, 'hot');
      setLeads(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch hot leads');
      console.error('Error fetching hot leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLeadSelect = (lead) => {
    navigate(`/leads/${lead.id}`);
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      <div className="bg-slate-700 px-6 py-4 border-b border-slate-600">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="text-2xl">🔴</span> Hot Leads
        </h2>
      </div>

      {error && (
        <div className="bg-red-900 text-red-200 px-6 py-4 border-b border-red-800">
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="px-6 py-8 text-center">
          <p className="text-slate-400">Loading hot leads...</p>
        </div>
      ) : leads.length === 0 ? (
        <div className="px-6 py-8 text-center">
          <p className="text-slate-400">No hot leads found</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700 border-b border-slate-600">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">LEAD</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">PHONE</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">EMAIL</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">STATUS</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">LAST CONTACT</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">ACTION</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id} className="border-b border-slate-700 hover:bg-red-900 hover:bg-opacity-20 transition">
                  <td className="px-6 py-4 text-white font-medium">
                    {lead.first_name} {lead.last_name || ''}
                  </td>
                  <td className="px-6 py-4 text-slate-300">{lead.phone}</td>
                  <td className="px-6 py-4 text-slate-300">{lead.email || '-'}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-red-700 text-white rounded text-xs font-medium">
                      {lead.status || 'pending'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {lead.updated_at ? formatInDubaiTz(lead.updated_at, 'date') :
                     lead.created_at ? formatInDubaiTz(lead.created_at, 'date') : '-'}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleLeadSelect(lead)}
                      className="text-yellow-400 hover:text-yellow-300 font-medium transition"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
