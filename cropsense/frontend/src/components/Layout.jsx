import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sprout, Sun, Moon } from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  const [isDark, setIsDark] = React.useState(false);

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Detect Disease', path: '/detect' },
    { name: 'Predict Yield', path: '/yield' },
    { name: 'Dashboard', path: '/dashboard' },
  ];

  return (
    <div className={isDark ? 'dark' : ''}>
      <div className="bg-background text-on-surface min-h-screen flex flex-col transition-colors duration-300">
        <header className="sticky top-0 w-full z-50 bg-surface/70 backdrop-blur-md">
          <nav className="flex justify-between items-center px-8 py-4 max-w-7xl mx-auto w-full">
            <Link to="/" className="text-2xl font-bold text-primary flex items-center gap-2 font-headline">
              <Sprout className="w-8 h-8 text-primary" fill="currentColor" />
              CropSense
            </Link>
            
            <div className="hidden md:flex gap-8 items-center">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`text-sm font-medium transition-colors ${
                    location.pathname === link.path
                      ? 'text-primary font-bold border-b-2 border-primary pb-1'
                      : 'text-on-surface-variant/70 hover:text-primary'
                  }`}
                >
                  {link.name}
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-4">
              <button 
                onClick={() => setIsDark(!isDark)}
                className="p-2 hover:bg-surface-container-high/50 rounded-lg transition-all scale-95 duration-200 ease-out"
              >
                {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
              <div className="md:hidden">
                {/* Mobile menu could go here */}
              </div>
            </div>
          </nav>
        </header>

        <main className="flex-grow w-full">
          {children}
        </main>

        <footer className="w-full bg-surface-container-low border-t border-surface-container-high/30">
          <div className="flex flex-col md:flex-row justify-between items-center px-8 py-8 w-full max-w-7xl mx-auto">
            <div className="flex flex-col items-center md:items-start gap-2 mb-6 md:mb-0">
              <div className="font-headline font-semibold text-on-surface flex items-center gap-2">
                <Sprout className="w-5 h-5 text-primary" />
                CropSense
              </div>
              <p className="font-body text-xs tracking-wide text-on-surface-variant/70">
                © 2026 CropSense. Organic Precision Agriculture. Created by Deepta Roy.
              </p>
            </div>
            
            <div className="flex flex-wrap justify-center gap-8">
              <a href="#" className="text-xs font-body tracking-wide text-on-surface-variant/70 hover:text-primary transition-opacity opacity-80 hover:opacity-100">Privacy Policy</a>
              <a href="#" className="text-xs font-body tracking-wide text-on-surface-variant/70 hover:text-primary transition-opacity opacity-80 hover:opacity-100">Terms of Service</a>
              <a href="#" className="text-xs font-body tracking-wide text-on-surface-variant/70 hover:text-primary transition-opacity opacity-80 hover:opacity-100">Contact Support</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
