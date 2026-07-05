import { Loader2 } from "lucide-react"

export default function RootLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="flex items-center gap-2 text-gray-600">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="text-sm font-medium">Loading...</span>
      </div>
    </div>
  )
}
