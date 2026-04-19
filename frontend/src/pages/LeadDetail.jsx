import { useParams, useNavigate } from 'react-router-dom';
import { useLead } from '../hooks/useLeads';
import { ChatViewer } from '../components/ChatViewer';
import { StatusBadge } from '../components/StatusBadge';

export default function LeadDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { lead, loading } = useLead(id);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>Loading lead...</p>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>Lead not found</p>
      </div>
    );
  }

  const qual = lead.qualifications?.[0] || {};

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            ← Back
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            {lead.first_name} {lead.last_name}
          </h1>
          <StatusBadge score={lead.score} />
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Chat Viewer */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border overflow-hidden">
            <div className="p-4 border-b bg-gray-50">
              <h2 className="font-semibold text-gray-900">Conversation</h2>
            </div>
            <ChatViewer leadId={id} />
          </div>
        </div>

        {/* Lead Details */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg border p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Lead Info</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-600">Phone</p>
                <p className="font-medium">{lead.phone}</p>
              </div>
              <div>
                <p className="text-gray-600">Email</p>
                <p className="font-medium">{lead.email || 'N/A'}</p>
              </div>
              <div>
                <p className="text-gray-600">Status</p>
                <p className="font-medium capitalize">{lead.status}</p>
              </div>
              <div>
                <p className="text-gray-600">Created</p>
                <p className="font-medium text-xs">
                  {new Date(lead.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Qualifications</h3>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-600">When Needed</p>
                <p className="font-medium">{qual.when_needed || 'Not yet'}</p>
              </div>
              <div>
                <p className="text-gray-600">Car Type</p>
                <p className="font-medium">{qual.car_type || 'Not yet'}</p>
              </div>
              <div>
                <p className="text-gray-600">Timeframe</p>
                <p className="font-medium capitalize">{qual.timeframe || 'Not yet'}</p>
              </div>
              <div>
                <p className="text-gray-600">Duration</p>
                <p className="font-medium">{qual.duration || 'Not yet'}</p>
              </div>
              {qual.special_notes && (
                <div>
                  <p className="text-gray-600">Notes</p>
                  <p className="font-medium text-xs">{qual.special_notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
