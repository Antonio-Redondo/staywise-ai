import React from 'react'
import './globals.css'
import ClientInit from './components/client-init'

export const metadata = {
  title: 'StayWiseAI — Find homes you will love',
  description: 'AI-powered housing recommendations tailored to how you want to live.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ClientInit />
        <div className="app-shell">
          <header className="site-header">
            <div className="brand">
              <span className="brand__mark">◆</span>
              <span className="brand__name">
                Stay<span>Wise</span>AI
              </span>
            </div>
            <nav className="site-header__nav">
              <a href="#">How it works</a>
              <a href="#">Neighborhoods</a>
              <a href="#">Saved</a>
            </nav>
          </header>
          {children}
          <footer className="site-footer">
            © {new Date().getFullYear()} StayWiseAI · Recommendations are informational only.
          </footer>
        </div>
      </body>
    </html>
  )
}
