import { clerkMiddleware } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const clerk = clerkMiddleware()

export default async function middleware(...args: Parameters<typeof clerk>) {
  if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    return NextResponse.next()
  }
  try {
    return await clerk(...args)
  } catch {
    return NextResponse.next()
  }
}

export const config = {
  matcher: [
    '/((?!_next|api|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/__clerk/(.*)',
  ],
}
