// Debug Google OAuth configuration
console.log('Environment check:');
console.log('VITE_GOOGLE_CLIENT_ID:', import.meta.env.VITE_GOOGLE_CLIENT_ID);
console.log('Current origin:', window.location.origin);
console.log('Current URL:', window.location.href);

// Check if Google script is loaded
if (window.google) {
  console.log('Google script loaded successfully');
} else {
  console.log('Google script NOT loaded');
}

export const debugGoogleOAuth = () => {
  console.log('Debug function called');
};
