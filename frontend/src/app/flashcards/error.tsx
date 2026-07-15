"use client"

export default function FlashcardsError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <aside className="w-64 border-r border-gray-200 bg-white p-4">
        <div className="flex items-center gap-2 px-3 py-4">
          <div className="h-8 w-8 rounded-lg bg-[#2563EB]" />
          <span className="text-lg font-bold text-[#0F172A]">Cognora</span>
        </div>
      </aside>
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-2xl pt-20 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Something went wrong</h1>
          <p className="mt-2 text-sm text-gray-600">
            {error.message || "An unexpected error occurred on the flashcards page."}
          </p>
          <button
            onClick={reset}
            className="mt-6 rounded-lg bg-[#2563EB] px-6 py-2 text-sm font-medium text-white hover:bg-[#1d4ed8]"
          >
            Try again
          </button>
        </div>
      </main>
    </div>
  )
}
