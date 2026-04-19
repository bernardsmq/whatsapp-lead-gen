export const UploadedLeadsPreview = ({ leads }) => {
  if (!leads || leads.length === 0) {
    return null;
  }

  // Get all unique columns from the leads data
  const columns = [...new Set(leads.flatMap(lead => Object.keys(lead)))];
  const displayColumns = ['first_name', 'last_name', 'phone', 'email', 'gender', 'nationality'];
  const relevantColumns = displayColumns.filter(col => columns.includes(col));

  return (
    <div className="mt-6 pt-6 border-t border-gray-200">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">📊</span>
        <h3 className="text-lg font-bold text-gray-900">Uploaded Leads Preview</h3>
        <span className="ml-auto bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-bold">
          {leads.length} lead{leads.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="overflow-x-auto bg-gray-50 rounded-lg border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-200 border-b border-gray-300">
            <tr>
              <th className="px-4 py-3 text-left font-bold text-gray-800 w-10">#</th>
              {relevantColumns.map((col) => (
                <th key={col} className="px-4 py-3 text-left font-bold text-gray-800 whitespace-nowrap">
                  {col
                    .replace(/_/g, ' ')
                    .split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {leads.map((lead, index) => (
              <tr key={index} className="border-b border-gray-200 hover:bg-blue-50 transition">
                <td className="px-4 py-3 text-gray-600 font-medium">{index + 1}</td>
                {relevantColumns.map((col) => (
                  <td key={col} className="px-4 py-3 text-gray-700">
                    {lead[col] ? String(lead[col]).substring(0, 30) : '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-xs text-blue-700">
          ℹ️ Review the data above before clicking "Start Workflow" to send WhatsApp messages
        </p>
      </div>
    </div>
  );
};
