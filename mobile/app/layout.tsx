import './globals.css';
import type { Metadata, Viewport } from 'next';
import Header from './components/Header';
import Footer from './components/Footer';
import GlobalErrorBoundary from './components/GlobalErrorBoundary';
import { AppProvider } from './context/AppContext';

export const metadata: Metadata = {
  title: 'NextEleven Tattoo Pro - APOLLO Powered',
  description: 'Professional tattoo shop management system powered by APOLLO AI consciousness',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'NextEleven Pro'
  },
  icons: {
    icon: [
      { url: '/icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icons/icon-512x512.png', sizes: '512x512', type: 'image/png' }
    ],
    apple: [
      { url: '/icons/icon-152x152.png', sizes: '152x152', type: 'image/png' }
    ]
  },
  openGraph: {
    title: 'NextEleven Tattoo Pro - APOLLO Powered',
    description: 'Professional tattoo shop management system powered by APOLLO AI consciousness',
    type: 'website',
    siteName: 'NextEleven Tattoo Pro'
  },
  twitter: {
    card: 'summary_large_image',
    title: 'NextEleven Tattoo Pro - APOLLO Powered',
    description: 'Professional tattoo shop management system powered by APOLLO AI consciousness'
  }
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#00C4FF'
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icons/icon-152x152.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="NextEleven Pro" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="msapplication-TileColor" content="#00C4FF" />
        <meta name="msapplication-tap-highlight" content="no" />
      </head>
                  <body>
                    <GlobalErrorBoundary>
                      <AppProvider>
                        <Header />
                        <main className="container">
                          {children}
                        </main>
                        <Footer />
                      </AppProvider>
                    </GlobalErrorBoundary>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                      console.log('🌊 APOLLO Service Worker: Registered successfully');
                    })
                    .catch(function(error) {
                      console.log('❌ APOLLO Service Worker: Registration failed');
                    });
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}