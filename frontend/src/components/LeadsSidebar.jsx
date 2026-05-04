import { useState } from 'react';
import { formatInDubaiTz } from '../lib/dateUtils';

export const LeadsSidebar = ({ leads, onSelectLead }) => {
  const [expandedLead, setExpandedLead] = useState(null);

  // Group leads by score
  const hotLeads = leads.filter(l => l.score === 'hot');
  const warmLeads = leads.filter(l => l.score === 'warm');
  const coldLeads = leads.filter(l => l.score === 'cold');

  const ScoreSection = ({ title, icon, color, leadsList }) => (
    <div className="mb-6">
      <div className={`bg-${color}-100 border-l-4 border-${color}-500 px-4 py-3 rounded mb-3`}>
        <h3 className={`font-bold text-${color}-900 flex items-center gap-2`}>
          <span className="text-lg">{icon}</span>
          {title}
          <span className={`ml-auto text-sm bg-${color}-200 px-2 py-1 rounded text-${color}-900`}>
            {leadsList.length}
          </span>
        </h3>
      </div>

      <div className="space-y-2">
        {leadsList.length === 0 ? (
          <p className="text-gray-400 text-sm px-3 py-2">No leads</p>
        ) : (
          leadsList.map(lead => (
            <div key={lead.id} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Lead Header - Clickable */}
              <button
                onClick={() => setExpandedLead(expandedLead === lead.id ? null : lead.id)}
                className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 transition flex items-center justify-between"
              >
                <div>
                  <p className="font-bold text-gray-900">{lead.first_name} {lead.last_name}</p>
                  <p className="text-xs text-gray-500">{lead.phone}</p>
                </div>
                <span className={`text-lg transition-transform ${expandedLead === lead.id ? 'rotate-180' : ''}`}>
                  ▼
                </span>
              </button>

              {/* Lead Details - Expandable */}
              {expandedLead === lead.id && (
                <div className="bg-white px-4 py-3 border-t border-gray-200 space-y-2 text-sm">
                  {lead.phone && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">📱 Phone:</span>
                      <span className="font-medium text-gray-900">{lead.phone}</span>
                    </div>
                  )}

                  {lead.email && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">📧 Email:</span>
                      <span className="font-medium text-gray-900">{lead.email}</span>
                    </div>
                  )}

                  {lead.first_name && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">👤 Name:</span>
                      <span className="font-medium text-gray-900">
                        {lead.first_name} {lead.last_name}
                      </span>
                    </div>
                  )}

                  {lead.gender && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">⚧ Gender:</span>
                      <span className="font-medium text-gray-900">{lead.gender}</span>
                    </div>
                  )}

                  {lead.nationality && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">🌍 Nationality:</span>
                      <span className="font-medium text-gray-900">{lead.nationality}</span>
                    </div>
                  )}

                  <div className="flex justify-between">
                    <span className="text-gray-600">📊 Status:</span>
                    <span className={`font-medium px-2 py-1 rounded text-xs ${
                      lead.status === 'contacted' ? 'bg-blue-100 text-blue-700' :
                      lead.status === 'qualified' ? 'bg-green-100 text-green-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {lead.status}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-gray-600">⭐ Score:</span>
                    <span className={`font-medium px-2 py-1 rounded text-xs ${
                      lead.score === 'hot' ? 'bg-red-100 text-red-700' :
                      lead.score === 'warm' ? 'bg-amber-100 text-amber-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {lead.score}
                    </span>
                  </div>

                  {lead.created_at && (
                    <div className="flex justify-between text-xs text-gray-500 pt-2 border-t">
                      <span>Added:</span>
                      <span>{formatInDubaiTz(lead.created_at, 'date')}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6 h-full overflow-y-auto">
      <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2 sticky top-0 bg-white pb-3 border-b">
        <span className="text-2xl">📋</span>
        All Leads
        <span className="ml-auto bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-bold">
          {leads.length}
        </span>
      </h2>

      <div className="space-y-6">
        <ScoreSection
          title="Hot Leads"
          icon="🔴"
          color="red"
          leadsList={hotLeads}
        />

        <ScoreSection
          title="Warm Leads"
          icon="🟡"
          color="amber"
          leadsList={warmLeads}
        />

        <ScoreSection
          title="Cold Leads"
          icon="⚪"
          color="gray"
          leadsList={coldLeads}
        />
      </div>
    </div>
  );
};
