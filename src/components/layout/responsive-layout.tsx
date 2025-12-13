import React from 'react';
import Navbar from '@/components/ui/navbar';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  showNavbar?: boolean;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ 
  children, 
  showNavbar = true 
}) => {
  return (
    <div className="min-h-screen bg-background">
      {showNavbar && <Navbar />}
      <main className={`${showNavbar ? 'pt-0' : ''}`}>
        <div className="container mx-auto px-10 py-6 max-w-10xl">
          {children}
        </div>
      </main>
    </div>
  );
};

export default ResponsiveLayout;