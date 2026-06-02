import React from 'react'
import '../styles/globals.css'

export const metadata = {
  title: 'StayWiseAI',
  description: 'Housing recommendations',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div style={{ maxWidth: 960, margin: '0 auto', padding: 20 }}>{children}</div>
      </body>
    </html>
  )
}
