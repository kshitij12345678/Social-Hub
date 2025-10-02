import React from 'react';
import { account } from '@/config/appwrite';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';

const GoogleAuthTest = () => {
  const { toast } = useToast();

  const testGoogleAuth = async () => {
    try {
      console.log('🔍 Testing Google OAuth...');
      
      // Direct call to createOAuth2Session (same as demo)
      (account as any).createOAuth2Session(
        "google",
        "http://localhost:8080", // success redirect (correct port)
        "http://localhost:8080"  // failure redirect
      );
      
      toast({
        title: "Google OAuth Initiated",
        description: "Redirecting to Google for authentication...",
      });
    } catch (error: any) {
      console.error('❌ Google OAuth Error:', error);
      toast({
        title: "Google OAuth Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const checkCurrentSession = async () => {
    try {
      const session = await account.get();
      console.log('✅ Current session:', session);
      toast({
        title: "Session Found",
        description: `Logged in as: ${session.email}`,
      });
    } catch (error: any) {
      console.log('ℹ️ No active session');
      toast({
        title: "No Active Session",
        description: "User is not logged in",
      });
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto mt-4">
      <CardHeader>
        <CardTitle>Google Auth Debug</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button 
          onClick={testGoogleAuth}
          className="w-full"
          style={{ background: "#4285F4", color: "white" }}
        >
          Test Google OAuth
        </Button>
        <Button 
          onClick={checkCurrentSession}
          variant="outline"
          className="w-full"
        >
          Check Current Session
        </Button>
        <p className="text-xs text-muted-foreground">
          Check browser console for detailed logs
        </p>
      </CardContent>
    </Card>
  );
};

export default GoogleAuthTest;
