import { useState } from 'react';
import axios from 'axios';

export const ManualLeadForm = ({ onSuccess }) => {
  const [firstName, setFirstName] = useState('');
  const [phone, setPhone] = useState('');
  const [carInterest, setCarInterest] = useState('');
  const [rentalDuration, setRentalDuration] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [newLead, setNewLead] = useState(null);
  const [sendingMessage, setSendingMessage] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/manual-leads/add`,
        {
          first_name: firstName,
          phone: phone,
          car_interest: carInterest,
          rental_duration: rentalDuration
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      setSuccess(true);
      // response.data contains: { message, lead_id, lead }
      console.log('✅ Lead added response:', response.data);
      const leadData = {
        id: response.data.lead_id || response.data.id,
        first_name: response.data.first_name || firstName,
        phone: response.data.phone || phone,
        ...response.data.lead
      };
      console.log('📍 Setting newLead:', leadData);
      setNewLead(leadData);
      setFirstName('');
      setPhone('');
      setCarInterest('');
      setRentalDuration('');
      if (onSuccess) {
        onSuccess(response.data);
      }

      // Keep showing success for 5 seconds, but don't clear the newLead
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add lead');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (leadId) => {
    setSendingMessage(true);
    try {
      console.log('📤 Sending WhatsApp to lead ID:', leadId);
      const token = localStorage.getItem('token');
      console.log('Token available:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN');

      const url = `${import.meta.env.VITE_API_URL}/workflows/start`;
      const payload = { lead_ids: [leadId] };

      console.log('Request URL:', url);
      console.log('Payload:', payload);

      const response = await axios.post(url, payload, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('✅ API Response:', response.data);
      alert('✅ WhatsApp message sent! Lead will respond on WhatsApp');
      setNewLead(null); // Clear the new lead after sending
    } catch (err) {
      console.error('❌ Send message error:', err);
      console.error('  Status:', err.response?.status);
      console.error('  Data:', err.response?.data);
      console.error('  Message:', err.message);
      alert('❌ Failed to send message: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSendingMessage(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-700 p-6 rounded-xl border border-slate-600">
      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">➕</span>
        Add Lead Manually
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <input
          type="text"
          placeholder="Name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
          className="px-4 py-2 border border-slate-600 rounded-lg bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
        />

        <input
          type="tel"
          placeholder="Phone Number"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          required
          className="px-4 py-2 border border-slate-600 rounded-lg bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
        />

        <input
          type="text"
          placeholder="Car Interest (optional)"
          value={carInterest}
          onChange={(e) => setCarInterest(e.target.value)}
          className="px-4 py-2 border border-slate-600 rounded-lg bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
        />

        <input
          type="text"
          placeholder="Rental Duration (optional)"
          value={rentalDuration}
          onChange={(e) => setRentalDuration(e.target.value)}
          className="px-4 py-2 border border-slate-600 rounded-lg bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`w-full px-4 py-2 rounded-lg font-bold transition-all ${
          loading
            ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
            : 'bg-yellow-500 text-slate-900 hover:bg-yellow-400'
        }`}
      >
        {loading ? 'Adding...' : 'Add Lead'}
      </button>

      {error && (
        <p className="mt-3 text-red-400 text-sm bg-red-900/20 p-3 rounded-lg border border-red-800">
          ❌ {error}
        </p>
      )}

      {success && (
        <p className="mt-3 text-green-400 text-sm bg-green-900/20 p-3 rounded-lg border border-green-800">
          ✅ Lead added successfully!
        </p>
      )}

      {newLead && (
        <div className="mt-6 p-4 bg-slate-800 rounded-lg border border-yellow-500">
          <div className="mb-3 text-xs text-slate-400">
            <p>Lead ID: {newLead.id}</p>
            <p>Name: {newLead.first_name} | Phone: {newLead.phone}</p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-semibold">
                {newLead.first_name || 'New Lead'}
              </p>
              <p className="text-slate-400 text-sm">{newLead.phone}</p>
            </div>
            <button
              onClick={() => {
                console.log('🔘 Send button clicked for lead:', newLead.id);
                handleSendMessage(newLead.id);
              }}
              disabled={sendingMessage}
              className={`px-4 py-2 rounded-lg font-bold transition-all whitespace-nowrap ml-4 ${
                sendingMessage
                  ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-500'
              }`}
            >
              {sendingMessage ? '📤 Sending...' : '📤 Send WhatsApp'}
            </button>
          </div>
        </div>
      )}
    </form>
  );
};
