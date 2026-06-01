import { SignIn } from '@clerk/nextjs'

export default function LoginPage() {
  return (
    <div className="min-h-screen gradient-hero flex items-center justify-center">
      <div className="animate-fade-in">
        <SignIn />
      </div>
    </div>
  )
}
