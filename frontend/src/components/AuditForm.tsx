"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle } from "lucide-react"

// Type definition for audit submission data
export type AuditSubmitData = {
  repoUrl: string
  pdfPath?: string
  mode: "detective" | "full"
}

interface AuditFormProps {
  onSubmit: (data: AuditSubmitData) => Promise<void>
  error?: boolean
  onRetry?: () => void
}

export function AuditForm({ onSubmit, error, onRetry }: AuditFormProps) {
  const [repoUrl, setRepoUrl] = useState("")
  const [pdfPath, setPdfPath] = useState("")
  const [mode, setMode] = useState<"detective" | "full">("full")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!repoUrl.trim()) return
    
    setLoading(true)
    try {
      await onSubmit({ repoUrl: repoUrl.trim(), pdfPath: pdfPath.trim() || undefined, mode })
    } catch (err) {
      console.error("Form submission error:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="max-w-2xl mx-auto bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Start New Audit</CardTitle>
        <CardDescription className="text-slate-400">
          Enter a GitHub repository URL to begin forensic code analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Repository URL */}
          <div className="space-y-2">
            <Label htmlFor="repoUrl" className="text-white">Repository URL *</Label>
            <Input
              id="repoUrl"
              type="url"
              placeholder="https://github.com/username/repo"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              required
              disabled={loading}
              className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500 focus:border-purple-500"
            />
          </div>

          {/* PDF Path (Optional) */}
          <div className="space-y-2">
            <Label htmlFor="pdfPath" className="text-white">Architecture Report PDF (Optional)</Label>
            <Input
              id="pdfPath"
              type="text"
              placeholder="reports/interim_report.pdf"
              value={pdfPath}
              onChange={(e) => setPdfPath(e.target.value)}
              disabled={loading}
              className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500 focus:border-purple-500"
            />
            <p className="text-sm text-slate-500">
              Path to PDF report for cross-reference verification
            </p>
          </div>

          {/* Audit Mode */}
          <div className="space-y-2">
            <Label className="text-white">Audit Mode</Label>
            <Select 
              value={mode} 
              onValueChange={(value: "detective" | "full") => setMode(value)}
              disabled={loading}
            >
              <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                <SelectValue placeholder="Select mode" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="detective" className="text-white hover:bg-slate-700 focus:bg-slate-700">
                  Detective Only (Interim)
                </SelectItem>
                <SelectItem value="full" className="text-white hover:bg-slate-700 focus:bg-slate-700">
                  Full Digital Courtroom (Final)
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-900/50 border border-red-700 rounded-lg">
              <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-red-200">Submission Failed</p>
                <p className="text-xs text-red-100/80 mt-1">
                  Please check the repository URL and try again. 
                  {onRetry && (
                    <button 
                      type="button"
                      onClick={onRetry}
                      className="underline ml-1 hover:text-red-100"
                    >
                      Retry
                    </button>
                  )}
                </p>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button 
            type="submit" 
            disabled={loading || !repoUrl.trim()}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
                Starting Audit...
              </span>
            ) : (
              "Run Audit"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}