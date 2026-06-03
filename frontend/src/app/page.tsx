import React from 'react'
import RecommendFlow from './components/recommend-flow'
import FtcDisclosure from './components/ftc-disclosure'

export default function Page() {
  return (
    <main>
      <h1>Find homes you will love</h1>
      <FtcDisclosure />
      <RecommendFlow />
    </main>
  )
}
