export default function Button({ 
  children, 
  variant = 'primary', 
  loading = false, 
  disabled = false, 
  ...props 
}) {
  const baseClasses = 'font-medium py-2 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2';
  
  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white disabled:bg-primary-400',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 disabled:bg-gray-100',
    danger: 'bg-red-600 hover:bg-red-700 text-white disabled:bg-red-400',
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {children}
    </button>
  );
}