"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { audioService, type AudioStatus } from "@/services/audio"
import { Sidebar } from "@/components/layout/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Mic, MicOff, Loader2, Upload, FileAudio, CheckCircle2, AlertCircle } from "lucide-react"
import { toast } from "sonner"

export default function RecordPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()

  const [recording, setRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [duration, setDuration] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState<AudioStatus | null>(null)
  const [pollingId, setPollingId] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!isAuthenticated) router.push("/login")
  }, [isAuthenticated, router])

  useEffect(() => {
    if (!pollingId) return
    const interval = setInterval(async () => {
      try {
        const result = await audioService.getStatus(pollingId)
        setStatus(result)
        if (result.processing_status === "completed" || result.processing_status === "failed") {
          clearInterval(interval)
          setPollingId(null)
        }
      } catch {
        clearInterval(interval)
        setPollingId(null)
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [pollingId])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" })
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })
        setAudioBlob(blob)
        stream.getTracks().forEach((t) => t.stop())
      }

      mediaRecorder.start()
      setRecording(true)
      setDuration(0)

      timerRef.current = setInterval(() => {
        setDuration((prev) => {
          if (prev >= 300) {
            stopRecording()
            return 300
          }
          return prev + 1
        })
      }, 1000)
    } catch {
      toast.error("Microphone access denied. Please allow microphone permissions.")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop()
    }
    setRecording(false)
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  const handleUpload = async () => {
    if (!audioBlob) return
    setUploading(true)
    try {
      const file = new File([audioBlob], `recording_${Date.now()}.webm`, { type: "audio/webm" })
      const result = await audioService.upload(file)
      setPollingId(result.id)
      setAudioBlob(null)
      setDuration(0)
      toast.success("Audio uploaded. Transcribing...")
    } catch (err: unknown) {
      const e = err as { message?: string }
      toast.error(e.message || "Failed to upload audio")
    } finally {
      setUploading(false)
    }
  }

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="lg:ml-64 p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="mx-auto max-w-2xl">
          <h1 className="text-2xl font-bold text-[#0F172A]">Audio Recording</h1>
          <p className="mt-1 text-sm text-gray-600">Record your study notes, answers, or explanations for AI transcription and feedback</p>

          <Card className="mt-6">
            <CardContent className="p-8 text-center">
              <div className={`mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full transition-colors ${recording ? "bg-red-50 animate-pulse" : "bg-gray-50"}`}>
                {recording ? (
                  <MicOff className="h-10 w-10 text-red-500 cursor-pointer" onClick={stopRecording} />
                ) : (
                  <Mic className="h-10 w-10 text-gray-400 cursor-pointer" onClick={startRecording} />
                )}
              </div>

              <h3 className="text-lg font-semibold text-[#0F172A]">
                {recording ? "Recording..." : audioBlob ? "Recording complete" : "Tap to start recording"}
              </h3>

              {recording && (
                <div className="mt-4">
                  <div className="flex items-center justify-center gap-2 text-sm">
                    <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                    <span className="text-gray-500">{Math.floor(duration / 60)}:{String(duration % 60).padStart(2, "0")} / 5:00</span>
                  </div>
                  <Progress value={(duration / 300) * 100} className="mt-2" indicatorClassName="bg-red-500" />
                </div>
              )}

              {audioBlob && !uploading && (
                <div className="mt-4">
                  <Badge variant="success" className="mb-3">
                    <CheckCircle2 className="mr-1 h-3 w-3" />
                    {duration}s recording ready
                  </Badge>
                  <div className="flex justify-center gap-3">
                    <Button variant="outline" onClick={() => { setAudioBlob(null); setDuration(0) }}>
                      Discard
                    </Button>
                    <Button onClick={handleUpload} className="gap-2">
                      <Upload className="h-4 w-4" />
                      Upload & Transcribe
                    </Button>
                  </div>
                </div>
              )}

              {recording && (
                <p className="mt-4 text-sm text-gray-400">Tap the microphone icon to stop</p>
              )}
            </CardContent>
          </Card>

          {uploading && (
            <Card className="mt-4">
              <CardContent className="flex items-center gap-3 p-4">
                <Loader2 className="h-5 w-5 animate-spin text-[#2563EB]" />
                <p className="text-sm text-gray-600">Uploading and processing audio...</p>
              </CardContent>
            </Card>
          )}

          {status && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileAudio className="h-5 w-5 text-[#2563EB]" />
                  Transcription Result
                  <Badge variant={status.processing_status === "completed" ? "success" : "secondary"}>
                    {status.processing_status}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {status.processing_status === "processing" && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Transcribing your audio...
                  </div>
                )}
                {status.processing_status === "failed" && (
                  <div className="flex items-center gap-2 text-sm text-red-500">
                    <AlertCircle className="h-4 w-4" />
                    Transcription failed. Please try again.
                  </div>
                )}
                {status.transcript && (
                  <div>
                    <h4 className="mb-2 text-sm font-medium text-gray-700">Transcript</h4>
                    <div className="rounded-lg bg-gray-50 p-4 text-sm text-gray-700">{status.transcript}</div>
                  </div>
                )}
                {status.ai_feedback && (
                  <div>
                    <h4 className="mb-2 text-sm font-medium text-gray-700">AI Feedback</h4>
                    <div className="rounded-lg bg-[#2563EB]/5 p-4 text-sm text-gray-700">{status.ai_feedback}</div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {!recording && !audioBlob && !uploading && !status && (
            <Card className="mt-6 border border-dashed border-gray-200">
              <CardContent className="p-6 text-center text-sm text-gray-400">
                <Upload className="mx-auto mb-2 h-6 w-6" />
                <p>You can also upload audio files directly from the Files page</p>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}
