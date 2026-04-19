import { useEffect, useRef } from 'react';
import { useConversations } from '../hooks/useLeads';
import { subscribeToConversations } from '../lib/supabase';

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

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {conversations.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-start' : 'justify-end'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-gray-100 text-gray-900'
                  : 'bg-blue-500 text-white'
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              <p className="text-xs mt-1 opacity-70">
                {new Date(msg.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
