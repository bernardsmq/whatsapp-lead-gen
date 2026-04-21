import { useState, useEffect } from 'react';
import { analyticsAPI } from '../lib/api';

export default function MessagesSent() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMessages();
  }, [selectedDate]);

  const fetchMessages = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await analyticsAPI.getMessagesByDate(selectedDate);
      setMessages(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch messages');
      console.error('Error fetching messages:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Messages Sent</h1>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600 hover:border-slate-500 transition"
        />
      </div>

      {error && (
        <div className="bg-red-900 text-red-200 px-6 py-4 rounded-lg border border-red-800 mb-6">
          <p>{error}</p>
        </div>
      )}

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="bg-slate-700 px-6 py-4 border-b border-slate-600">
          <p className="text-slate-300">
            Showing {messages.length} message{messages.length !== 1 ? 's' : ''} for {selectedDate}
          </p>
        </div>

        <div className="divide-y divide-slate-700">
          {loading ? (
            <div className="px-6 py-8 text-center">
              <p className="text-slate-400">Loading messages...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <p className="text-slate-400">No messages for this date</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className="px-6 py-4 hover:bg-slate-700 transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-semibold text-white">{msg.lead_name}</p>
                    <p className="text-sm text-slate-400">{msg.lead_phone}</p>
                    <p className="text-slate-300 mt-2">{msg.message}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className={`inline-block px-3 py-1 rounded text-xs font-medium ${
                      msg.sender === 'ai' ? 'bg-yellow-600 text-white' : 'bg-slate-600 text-slate-300'
                    }`}>
                      {msg.sender === 'ai' ? '🤖 Sent' : '📩 Received'}
                    </span>
                    <p className="text-xs text-slate-500 mt-2">✓ {msg.delivery_status || 'delivered'}</p>
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
