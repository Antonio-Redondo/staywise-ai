import React from 'react'
import ClientInit from './components/client-init'

export const metadata = {
  title: 'StayWiseAI',
  description: 'Housing recommendations',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ClientInit />
        <div style={{ maxWidth: 960, margin: '0 auto', padding: 20 }}>{children}</div>
      </body>
    </html>
  )
}
