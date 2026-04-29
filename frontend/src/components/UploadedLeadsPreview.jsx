import { useState } from 'react';
import { whatsappAPI } from '../lib/api';

export const UploadedLeadsPreview = ({ leads }) => {
  const [isSending, setIsSending] = useState(false);
  const [sendResults, setSendResults] = useState(null);
  const [sendProgress, setSendProgress] = useState(null);

  if (!leads || leads.length === 0) {
    return null;
  }

  const handleSendAll = async () => {
    if (!window.confirm(`Send WhatsApp messages to all ${leads.length} leads?`)) {
      return;
    }

    setIsSending(true);
    setSendProgress(0);
    setSendResults(null);

    try {
      const response = await whatsappAPI.sendBulk(leads);
      setSendResults(response.data);
      setSendProgress(100);
    } catch (error) {
      alert(`Error sending messages: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="mt-6 pt-6 border-t border-gray-200">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">📊</span>
        <h3 className="text-lg font-bold text-gray-900">Uploaded Leads Preview</h3>
        <span className="ml-auto bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-bold">
          {leads.length} lead{leads.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Preview Table */}
      <div className="overflow-x-auto bg-gray-50 rounded-lg border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-200 border-b border-gray-300">
            <tr>
              <th className="px-4 py-3 text-left font-bold text-gray-800 w-10">#</th>
              <th className="px-4 py-3 text-left font-bold text-gray-800">Name</th>
              <th className="px-4 py-3 text-left font-bold text-gray-800">Phone</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead, index) => (
              <tr key={index} className="border-b border-gray-200 hover:bg-blue-50 transition">
                <td className="px-4 py-3 text-gray-600 font-medium">{index + 1}</td>
                <td className="px-4 py-3 text-gray-700">
                  {lead.name || '-'}
                </td>
                <td className="px-4 py-3 text-gray-700">
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
          className="px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {isSending ? '⏳ Sending...' : '✉️ Send WhatsApp to All'}
        </button>
      </div>

      {/* Info Box */}
      <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-xs text-blue-700">
          ℹ️ Click "Send WhatsApp to All" to send the template message to all {leads.length} leads
        </p>
      </div>

      {/* Results Display */}
      {sendResults && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">✅</span>
            <h3 className="text-lg font-bold text-gray-900">Send Results</h3>
            <span className="ml-auto text-sm font-bold">
              <span className="text-green-600">Sent: {sendResults.sent}</span>
              {' / '}
              <span className="text-red-600">Failed: {sendResults.failed}</span>
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg border border-gray-200 max-h-64 overflow-y-auto">
            {sendResults.results && sendResults.results.map((result, index) => (
              <div key={index} className={`px-4 py-2 border-b border-gray-200 text-sm ${result.status === 'sent' ? 'bg-green-50' : 'bg-red-50'}`}>
                <div className="flex items-center gap-2">
                  <span>{result.status === 'sent' ? '✅' : '❌'}</span>
                  <span className="font-semibold flex-1">{result.name}</span>
                  <span className="text-gray-600">{result.phone}</span>
                  {result.error && <span className="text-red-600 text-xs">{result.error}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
