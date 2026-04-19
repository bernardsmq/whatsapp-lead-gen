import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_KEY;

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Real-time subscription helper
export const subscribeToConversations = (leadId, callback) => {
  return supabase
    .channel(`conversations:${leadId}`)
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'conversations',
      filter: `lead_id=eq.${leadId}`,
    }, callback)
    .subscribe();
};

export const subscribeToLeads = (callback) => {
  return supabase
    .channel('leads')
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'leads',
    }, callback)
    .subscribe();
};
