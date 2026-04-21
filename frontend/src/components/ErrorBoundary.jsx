import { Component } from 'react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-xl border border-red-700 p-8 max-w-md text-center">
            <p className="text-red-400 font-bold mb-4">⚠️ Something went wrong</p>
            <p className="text-slate-300 text-sm mb-6">{this.state.error?.message}</p>
            <button
              onClick={() => {
                localStorage.removeItem('token');
                localStorage.removeItem('user_id');
                window.location.href = '/login';
              }}
              className="px-4 py-2 bg-yellow-500 text-slate-900 rounded font-bold hover:bg-yellow-400"
            >
              Go to Login
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
