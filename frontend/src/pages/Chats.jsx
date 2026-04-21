import { useState, useEffect } from 'react';
import { leadsAPI } from '../lib/api';

export default function Chats() {
  const [leads, setLeads] = useState([]);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loadingLeads, setLoadingLeads] = useState(true);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    setLoadingLeads(true);
    setError(null);
    try {
      const response = await leadsAPI.getAll();
      setLeads(response.data || []);
      // Select first lead by default
      if (response.data && response.data.length > 0) {
        setSelectedLeadId(response.data[0].id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch leads');
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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-screen">
      {/* Leads List */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden flex flex-col">
        <div className="bg-slate-700 px-6 py-4 border-b border-slate-600">
          <h2 className="text-xl font-bold text-white">Chats</h2>
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
          ) : (
            <div className="divide-y divide-slate-700">
              {leads.map((lead) => (
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
                  {conversations.map((conv) => (
                    <div
                      key={conv.id}
                      className={`flex gap-3 ${
                        conv.sender === 'ai' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <div
                        className={`max-w-xs px-4 py-2 rounded-lg ${
                          conv.sender === 'ai'
                            ? 'bg-yellow-600 text-white rounded-br-none'
                            : 'bg-slate-700 text-slate-200 rounded-bl-none'
                        }`}
                      >
                        <p className="text-sm">{conv.content}</p>
                        <p className={`text-xs mt-1 ${
                          conv.sender === 'ai'
                            ? 'text-yellow-100'
                            : 'text-slate-400'
                        }`}>
                          {new Date(conv.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
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
