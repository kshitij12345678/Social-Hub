import { useEffect } from 'react';

const GoogleAuthTest = () => {
  useEffect(() => {
    console.log('=== Google OAuth Debug Info ===');
    console.log('Client ID from env:', import.meta.env.VITE_GOOGLE_CLIENT_ID);
    console.log('Current origin:', window.location.origin);
    console.log('Google object available:', !!window.google);
    
    if (window.google) {
      console.log('Google accounts available:', !!window.google.accounts);
    }
  }, []);

  return (
    <div className="p-8 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Google Auth Test</h2>
      <div className="space-y-2 text-sm">
        <p><strong>Client ID:</strong> {import.meta.env.VITE_GOOGLE_CLIENT_ID}</p>
        <p><strong>Origin:</strong> {window.location.origin}</p>
        <p><strong>Google loaded:</strong> {window.google ? 'Yes' : 'No'}</p>
      </div>
      
      <div className="mt-6">
        <h3 className="font-semibold mb-2">Required Google Console Settings:</h3>
        <ul className="text-sm space-y-1 list-disc list-inside">
          <li>Authorized JavaScript origins: <code>{window.location.origin}</code></li>
          <li>OAuth consent screen must be configured</li>
          <li>Client ID must match exactly</li>
        </ul>
      </div>
    </div>
  );
};

export default GoogleAuthTest;
