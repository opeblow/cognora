"use client"

export default function ResetPasswordError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC]">
      <div className="mx-auto max-w-md px-6 text-center">
        <div className="mx-auto mb-6 h-12 w-12 rounded-lg bg-[#2563EB]" />
        <h1 className="text-2xl font-bold text-gray-900">Something went wrong</h1>
        <p className="mt-2 text-sm text-gray-600">
          {error.message || "An unexpected error occurred. Please try again."}
        </p>
        <button
          onClick={reset}
          className="mt-6 rounded-lg bg-[#2563EB] px-6 py-2 text-sm font-medium text-white hover:bg-[#1d4ed8]"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
