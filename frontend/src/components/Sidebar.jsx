import { useState } from 'react';

export default function Sidebar({ currentPage, setCurrentPage, onLogout }) {
  const [isExpanded, setIsExpanded] = useState(true);

  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'import', icon: '📤', label: 'Import Leads' },
    { id: 'all-leads', icon: '📋', label: 'All Leads' },
    { id: 'hot-leads', icon: '🔴', label: 'Hot Leads' },
    { id: 'warm-leads', icon: '🟡', label: 'Warm Leads' },
    { id: 'cold-leads', icon: '⚪', label: 'Cold Leads' },
    { id: 'chats', icon: '💬', label: 'Chats' },
    { id: 'messages', icon: '✉️', label: 'Messages Sent' },
    { id: 'analytics', icon: '📈', label: 'Analytics' },
    { id: 'settings', icon: '⚙️', label: 'Settings' },
  ];

  return (
    <div className={`fixed left-0 top-0 h-screen bg-slate-900 border-r border-slate-700 z-50 transition-all duration-300 ${
      isExpanded ? 'w-64' : 'w-20'
    }`}>
      {/* Logo */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-lg flex items-center justify-center font-bold text-slate-900">
            RCR
          </div>
          {isExpanded && (
            <div>
              <p className="font-bold text-white text-sm">RCR AI</p>
              <p className="text-xs text-slate-400">Lead Gen</p>
            </div>
          )}
        </div>
      </div>

      {/* Menu Items */}
      <nav className="p-4 space-y-2 overflow-y-auto max-h-[calc(100vh-200px)]">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              currentPage === item.id
                ? 'bg-yellow-500 text-slate-900 font-semibold'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
            title={isExpanded ? '' : item.label}
          >
            <span className="text-xl flex-shrink-0">{item.icon}</span>
            {isExpanded && <span className="text-sm">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700 space-y-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-all text-sm"
        >
          <span>{isExpanded ? '◀' : '▶'}</span>
          {isExpanded && 'Collapse'}
        </button>
        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-all text-sm"
        >
          <span>🚪</span>
          {isExpanded && 'Logout'}
        </button>
      </div>
    </div>
  );
}
