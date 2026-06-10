import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'
const API_KEY = process.env.API_KEY || ''

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const res = await fetch(`${BACKEND_URL}/conversation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify(body),
    })
    const data = await res.json().catch(() => ({ detail: 'Invalid response from backend' }))
    return NextResponse.json(data, { status: res.status })
  } catch {
    return NextResponse.json({ detail: 'Failed to reach backend' }, { status: 502 })
  }
}
