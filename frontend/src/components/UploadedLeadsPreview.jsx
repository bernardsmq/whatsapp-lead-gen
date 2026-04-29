import { useState } from 'react';
import { whatsappAPI } from '../lib/api';

export const UploadedLeadsPreview = ({ leads }) => {
  const [isSending, setIsSending] = useState(false);
  const [sendResults, setSendResults] = useState(null);

  if (!leads || leads.length === 0) {
    return null;
  }

  const handleSendAll = async () => {
    if (!window.confirm(`Send WhatsApp messages to all ${leads.length} leads?`)) {
      return;
    }

    setIsSending(true);
    setSendResults(null);

    try {
      const response = await whatsappAPI.sendBulk(leads);
      setSendResults(response.data);
    } catch (error) {
      alert(`Error sending messages: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="mt-6 pt-6 border-t border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">📊</span>
        <h3 className="text-lg font-bold text-white">Uploaded Leads Preview</h3>
        <span className="ml-auto bg-blue-900 text-blue-200 px-3 py-1 rounded-full text-sm font-bold">
          {leads.length} lead{leads.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Preview Table */}
      <div className="overflow-x-auto bg-slate-700 rounded-lg border border-slate-600">
        <table className="w-full text-sm">
          <thead className="bg-slate-800 border-b border-slate-600">
            <tr>
              <th className="px-4 py-3 text-left font-bold text-white w-10">#</th>
              <th className="px-4 py-3 text-left font-bold text-white">Name</th>
              <th className="px-4 py-3 text-left font-bold text-white">Phone</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead, index) => (
              <tr key={index} className="border-b border-slate-600 hover:bg-slate-600 transition">
                <td className="px-4 py-3 text-slate-300 font-medium">{index + 1}</td>
                <td className="px-4 py-3 text-slate-200">
                  {lead.name || '-'}
                </td>
                <td className="px-4 py-3 text-slate-200">
                  {lead.phone || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Action Button */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={handleSendAll}
          disabled={isSending}
          className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition"
        >
          {isSending ? '⏳ Sending...' : `✉️ Send WhatsApp to All (${leads.length})`}
        </button>
      </div>

      {/* Info Box */}
      <div className="mt-3 p-3 bg-blue-900/30 rounded-lg border border-blue-700">
        <p className="text-xs text-blue-300">
          ℹ️ Click "Send WhatsApp to All" to send the template message to all {leads.length} leads
        </p>
      </div>

      {/* Results Display */}
      {sendResults && (
        <div className="mt-6 pt-6 border-t border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">✅</span>
            <h3 className="text-lg font-bold text-white">Send Results</h3>
            <span className="ml-auto text-sm font-bold">
              <span className="text-green-400">Sent: {sendResults.sent}</span>
              {' / '}
              <span className="text-red-400">Failed: {sendResults.failed}</span>
            </span>
          </div>

          <div className="bg-slate-700 rounded-lg border border-slate-600 max-h-64 overflow-y-auto">
            {sendResults.results && sendResults.results.map((result, index) => (
              <div key={index} className={`px-4 py-2 border-b border-slate-600 text-sm ${result.status === 'sent' ? 'bg-green-900/20' : 'bg-red-900/20'}`}>
                <div className="flex items-center gap-2">
                  <span>{result.status === 'sent' ? '✅' : '❌'}</span>
                  <span className="font-semibold flex-1 text-white">{result.name}</span>
                  <span className="text-slate-400">{result.phone}</span>
                  {result.error && <span className="text-red-400 text-xs">{result.error}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
