import { useState } from 'react';
import { StatusBadge } from './StatusBadge';

export const LeadsTable = ({ leads, loading, onSelectLead }) => {
  const [sortBy, setSortBy] = useState('created_at');
  const [filterScore, setFilterScore] = useState(null);

  const filteredLeads = filterScore
    ? leads.filter((lead) => lead.score === filterScore)
    : leads;

  const sortedLeads = [...filteredLeads].sort((a, b) => {
    if (sortBy === 'name') {
      return a.first_name.localeCompare(b.first_name);
    }
    return new Date(b[sortBy]) - new Date(a[sortBy]);
  });

  if (loading) {
    return <div className="p-4">Loading leads...</div>;
  }

  if (sortedLeads.length === 0) {
    return <div className="p-4 text-gray-500">No leads found</div>;
  }

  return (
    <div className="bg-white rounded-lg border overflow-hidden">
      <div className="p-4 border-b flex gap-4">
        <select
          value={filterScore || ''}
          onChange={(e) => setFilterScore(e.target.value || null)}
          className="px-3 py-2 border rounded-lg text-sm"
        >
          <option value="">All Scores</option>
          <option value="hot">Hot 🔴</option>
          <option value="warm">Warm 🟡</option>
          <option value="cold">Cold ⚪</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-2 border rounded-lg text-sm"
        >
          <option value="created_at">Latest First</option>
          <option value="name">Name</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Name</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Phone</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Score</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">Status</th>
            </tr>
          </thead>
          <tbody>
            {sortedLeads.map((lead) => (
              <tr
                key={lead.id}
                className="border-b hover:bg-gray-50 cursor-pointer"
                onClick={() => onSelectLead(lead)}
              >
                <td className="px-6 py-4">{lead.first_name} {lead.last_name}</td>
                <td className="px-6 py-4 text-gray-600">{lead.phone}</td>
                <td className="px-6 py-4">
                  <StatusBadge score={lead.score} />
                </td>
                <td className="px-6 py-4 text-gray-600">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                    {lead.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
