"use client"

export default function RootError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-bold text-gray-900">Something went wrong</h1>
        <p className="mt-2 text-sm text-gray-600">
          An unexpected error occurred. Please try again.
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
