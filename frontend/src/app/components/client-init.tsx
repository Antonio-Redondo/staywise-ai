"use client"
import React, { useEffect } from 'react'
import { initObservability } from '@/lib/observability'

export default function ClientInit() {
  useEffect(() => {
    void initObservability()
  }, [])

  return null
}
