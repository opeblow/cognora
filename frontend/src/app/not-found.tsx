import Link from "next/link"

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="max-w-md text-center">
        <h1 className="text-6xl font-bold text-[#2563EB]">404</h1>
        <p className="mt-4 text-lg font-semibold text-gray-900">Page not found</p>
        <p className="mt-2 text-sm text-gray-600">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-lg bg-[#2563EB] px-6 py-2 text-sm font-medium text-white hover:bg-[#1d4ed8]"
        >
          Go home
        </Link>
      </div>
    </div>
  )
}
