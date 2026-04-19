export const StatusBadge = ({ score }) => {
  const styles = {
    hot: 'bg-red-100 text-red-800',
    warm: 'bg-amber-100 text-amber-800',
    cold: 'bg-gray-100 text-gray-800',
  };

  const icons = {
    hot: '🔴',
    warm: '🟡',
    cold: '⚪',
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${styles[score] || styles.cold}`}>
      {icons[score]} {score?.toUpperCase() || 'UNKNOWN'}
    </span>
  );
};
