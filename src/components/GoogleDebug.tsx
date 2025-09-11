import React, { useEffect } from 'react';

export const GoogleDebug = () => {
  useEffect(() => {
    console.log('=== GOOGLE DEBUG INFO ===');
    console.log('Environment Client ID:', import.meta.env.VITE_GOOGLE_CLIENT_ID);
    console.log('Current Origin:', window.location.origin);
    console.log('Google object available:', !!window.google);
    console.log('All environment variables:', import.meta.env);
    
    // Test Google initialization
    if (window.google) {
      try {
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          callback: (response: any) => {
            console.log('Google callback received:', response);
          },
        });
        console.log('Google initialization successful');
      } catch (error) {
        console.error('Google initialization failed:', error);
      }
    }
  }, []);

  return (
    <div className="p-4 bg-yellow-100 border border-yellow-400 rounded">
      <h3 className="font-bold text-yellow-800">Google OAuth Debug Info:</h3>
      <p><strong>Client ID:</strong> {import.meta.env.VITE_GOOGLE_CLIENT_ID}</p>
      <p><strong>Current Origin:</strong> {window.location.origin}</p>
      <p><strong>Google Loaded:</strong> {window.google ? 'Yes' : 'No'}</p>
    </div>
  );
};

export default GoogleDebug;
