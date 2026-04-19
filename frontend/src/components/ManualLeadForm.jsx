import { useState } from 'react';
import axios from 'axios';

export const ManualLeadForm = ({ onSuccess }) => {
  const [firstName, setFirstName] = useState('');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

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
          phone: phone
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      setSuccess(true);
      setFirstName('');
      setPhone('');
      if (onSuccess) {
        onSuccess(response.data);
      }

      // Clear success message after 2 seconds
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add lead');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-blue-50 p-6 rounded-lg border border-blue-200">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span className="text-2xl">➕</span>
        Add Lead Manually (for testing)
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <input
          type="text"
          placeholder="First Name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <input
          type="tel"
          placeholder="Phone Number (e.g., +37124811178)"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          required
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`w-full px-4 py-2 rounded-lg font-bold transition-all ${
          loading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {loading ? 'Adding...' : 'Add Lead'}
      </button>

      {error && (
        <p className="mt-3 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
          ❌ {error}
        </p>
      )}

      {success && (
        <p className="mt-3 text-green-600 text-sm bg-green-50 p-3 rounded-lg">
          ✅ Lead added successfully!
        </p>
      )}
    </form>
  );
};
