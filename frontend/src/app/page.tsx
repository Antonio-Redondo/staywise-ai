import React from 'react'
import RecommendFlow from './components/recommend-flow'
import FtcDisclosure from './components/ftc-disclosure'

export default function Page() {
  return (
    <main>
      <section className="hero">
        <span className="hero__eyebrow">✦ AI-matched listings</span>
        <h1>
          Find homes <span>you will love</span>
        </h1>
        <p className="hero__sub">
          Describe your ideal place. StayWiseAI reads your intent, scores
          neighborhoods, and surfaces listings that actually fit your life.
        </p>
      </section>
      <RecommendFlow />
      <FtcDisclosure />
    </main>
  )
}
