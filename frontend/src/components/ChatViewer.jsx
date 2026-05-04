import { useEffect, useRef } from 'react';
import { useConversations } from '../hooks/useLeads';
import { subscribeToConversations } from '../lib/supabase';
import { formatInDubaiTz } from '../lib/dateUtils';

export const ChatViewer = ({ leadId }) => {
  const { conversations, loading } = useConversations(leadId);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations]);

  useEffect(() => {
    if (!leadId) return;

    let subscription;

    const setupSubscription = async () => {
      subscription = await subscribeToConversations(leadId, () => {
        // Conversation updated - hook will refetch
      });
    };

    setupSubscription();

    return () => {
      if (subscription) {
        subscription.unsubscribe();
      }
    };
  }, [leadId]);

  if (loading) return <div className="p-4">Loading conversations...</div>;

  if (!conversations.length) {
    return <div className="p-4 text-gray-500">No messages yet</div>;
  }

  // Helper function to get status badge icon and color
  const getStatusBadge = (status) => {
    switch(status) {
      case 'read':
        return { icon: '✓✓', color: 'text-blue-600' };
      case 'delivered':
        return { icon: '✓', color: 'text-green-600' };
      case 'failed':
        return { icon: '✗', color: 'text-red-600' };
      case 'sent':
      case 'pending':
        return { icon: '⏱', color: 'text-gray-500' };
      default:
        return { icon: '◦', color: 'text-gray-400' };
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {conversations.map((msg) => {
          const isTemplate = msg.sender === 'template';
          const statusBadge = getStatusBadge(msg.delivery_status);

          return (
            <div
              key={msg.id}
              className={`flex ${msg.sender === 'user' ? 'justify-start' : 'justify-end'}`}
            >
              <div className="flex flex-col max-w-xs">
                <div
                  className={`px-4 py-2 rounded-lg ${
                    isTemplate
                      ? 'bg-purple-100 text-purple-900 border border-purple-300'
                      : msg.sender === 'user'
                      ? 'bg-gray-100 text-gray-900'
                      : 'bg-blue-500 text-white'
                  }`}
                >
                  {isTemplate && <p className="text-xs font-semibold mb-1">📋 Template Message</p>}
                  <p className="text-sm">{msg.content}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <p className={`text-xs opacity-70`}>
                      {formatInDubaiTz(msg.created_at, 'time')}
                    </p>
                    {msg.delivery_status && (
                      <p className={`text-xs font-bold ${statusBadge.color}`}>
                        {statusBadge.icon}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
