import { useState, useEffect } from 'react';
import { leadsAPI } from '../lib/api';

export default function Chats() {
  const [leads, setLeads] = useState([]);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loadingLeads, setLoadingLeads] = useState(true);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Test API connection first
    const testConnection = async () => {
      try {
        console.log('Testing API connection...');
        const api = (await import('../lib/api')).default;
        const healthCheck = await api.get('/health');
        console.log('✓ API health check passed:', healthCheck.data);
      } catch (err) {
        console.error('✗ API health check failed:', err.message);
      }
      fetchLeads();
    };
    testConnection();
  }, []);

  const fetchLeads = async () => {
    setLoadingLeads(true);
    setError(null);
    try {
      const response = await leadsAPI.getAll();
      const leadsData = response.data.leads || response.data || [];
      setLeads(leadsData);
      // Select first lead by default
      if (leadsData && leadsData.length > 0) {
        setSelectedLeadId(leadsData[0].id);
      }
    } catch (err) {
      console.error('Full error object:', err);
      console.error('Error response:', err.response);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch leads';
      setError(`Error: ${errorMsg} (Check console for details)`);
      console.error('Error fetching leads:', err);
    } finally {
      setLoadingLeads(false);
    }
  };

  const fetchConversations = async (leadId) => {
    setLoadingConversations(true);
    setError(null);
    try {
      const response = await leadsAPI.getConversations(leadId);
      setConversations(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch conversations');
      console.error('Error fetching conversations:', err);
    } finally {
      setLoadingConversations(false);
    }
  };

  const handleLeadSelect = (leadId) => {
    setSelectedLeadId(leadId);
    fetchConversations(leadId);
  };

  const selectedLead = leads.find(l => l.id === selectedLeadId);

  // Filter leads based on search query
  const filteredLeads = leads.filter(lead => {
    const searchLower = searchQuery.toLowerCase();
    const fullName = `${lead.first_name || ''} ${lead.last_name || ''}`.toLowerCase();
    const phone = (lead.phone || '').toLowerCase();
    return fullName.includes(searchLower) || phone.includes(searchLower);
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-screen">
      {/* Leads List */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden flex flex-col">
        <div className="bg-slate-700 px-6 py-4 border-b border-slate-600 space-y-3">
          <h2 className="text-xl font-bold text-white">Chats</h2>
          <input
            type="text"
            placeholder="Search by name or phone..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition text-sm"
          />
          {leads.length > 0 && (
            <p className="text-xs text-slate-300">
              Showing {filteredLeads.length} of {leads.length} chats
            </p>
          )}
        </div>

        {error && (
          <div className="bg-red-900 text-red-200 px-6 py-3 border-b border-red-800 text-sm">
            {error}
          </div>
        )}

        <div className="flex-1 overflow-y-auto">
          {loadingLeads ? (
            <div className="px-6 py-8 text-center">
              <p className="text-slate-400">Loading chats...</p>
            </div>
          ) : leads.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <p className="text-slate-400">No chats available</p>
            </div>
          ) : filteredLeads.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <p className="text-slate-400">No chats match "{searchQuery}"</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-700">
              {filteredLeads.map((lead) => (
                <button
                  key={lead.id}
                  onClick={() => handleLeadSelect(lead.id)}
                  className={`w-full px-6 py-4 text-left transition ${
                    selectedLeadId === lead.id
                      ? 'bg-yellow-600 border-l-4 border-yellow-400'
                      : 'hover:bg-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-white truncate">
                        {lead.first_name} {lead.last_name || ''}
                      </p>
                      <p className="text-sm text-slate-300 truncate">{lead.phone}</p>
                    </div>
                    <span className={`flex-shrink-0 px-2 py-1 rounded-full text-xs font-bold whitespace-nowrap ${
                      lead.score === 'hot' ? 'bg-red-600 text-white' :
                      lead.score === 'warm' ? 'bg-yellow-500 text-white' :
                      'bg-slate-600 text-slate-300'
                    }`}>
                      {lead.score || 'cold'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Conversation View */}
      <div className="lg:col-span-2 bg-slate-800 rounded-xl border border-slate-700 overflow-hidden flex flex-col">
        {selectedLead ? (
          <>
            <div className="bg-slate-700 px-6 py-4 border-b border-slate-600">
              <h2 className="text-xl font-bold text-white">
                {selectedLead.first_name} {selectedLead.last_name || ''}
              </h2>
              <p className="text-sm text-slate-400">{selectedLead.phone}</p>
            </div>

            <div className="flex-1 overflow-y-auto">
              {loadingConversations ? (
                <div className="flex items-center justify-center h-full">
                  <p className="text-slate-400">Loading messages...</p>
                </div>
              ) : conversations.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <p className="text-slate-400">No messages yet</p>
                </div>
              ) : (
                <div className="p-6 space-y-4">
                  {conversations.map((conv) => {
                    const isTemplate = conv.sender === 'template';
                    const statusMap = {
                      'read': { icon: '✓✓', color: 'text-blue-400' },
                      'delivered': { icon: '✓', color: 'text-green-400' },
                      'failed': { icon: '✗', color: 'text-red-400' },
                      'sent': { icon: '⏱', color: 'text-gray-400' },
                      'pending': { icon: '⏱', color: 'text-gray-400' },
                    };
                    const status = statusMap[conv.delivery_status] || { icon: '◦', color: 'text-gray-500' };

                    return (
                      <div
                        key={conv.id}
                        className={`flex gap-3 ${
                          (conv.sender === 'ai' || isTemplate) ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div className="flex flex-col max-w-xs">
                          <div
                            className={`px-4 py-2 rounded-lg ${
                              isTemplate
                                ? 'bg-purple-700 text-purple-100 rounded-br-none border border-purple-600'
                                : conv.sender === 'ai'
                                ? 'bg-yellow-600 text-white rounded-br-none'
                                : 'bg-slate-700 text-slate-200 rounded-bl-none'
                            }`}
                          >
                            {isTemplate && <p className="text-xs font-semibold mb-1">📋 Template</p>}
                            <p className="text-sm">{conv.content}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <p className={`text-xs ${
                                conv.sender === 'ai'
                                  ? 'text-yellow-100'
                                  : isTemplate
                                  ? 'text-purple-200'
                                  : 'text-slate-400'
                              }`}>
                                {new Date(conv.created_at).toLocaleTimeString()}
                              </p>
                              {conv.delivery_status && (
                                <p className={`text-xs font-bold ${status.color}`}>
                                  {status.icon}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-slate-400">Select a chat to view messages</p>
          </div>
        )}
      </div>
    </div>
  );
}
