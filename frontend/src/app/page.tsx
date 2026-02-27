"use client"

import { useState, useEffect, useCallback } from "react"
import { AuditForm } from "@/components/AuditForm"
import { ResultsViewer } from "@/components/ResultsViewer"

// Type definition for audit submission
type AuditSubmitData = {
  repoUrl: string
  pdfPath?: string
  mode: "detective" | "full"
}

// Type definition for audit result
type AuditResult = {
  audit_id: string
  overall_score: number
  criteria_evaluated: number
  executive_summary: string
  criteria: Array<{
    dimension_id: string
    dimension_name: string
    final_score: number
    judge_opinions: Array<{
      judge: string
      score: number
      argument: string
    }>
    remediation: string
  }>
  remediation_plan: string
  report_markdown: string
}

export default function Home() {
  const [auditId, setAuditId] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "processing" | "completed" | "error">("idle")
  const [result, setResult] = useState<AuditResult | null>(null)

  const pollForResults = useCallback(async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/audit/${id}`)
        const data = await response.json()
        
        if (data.status === "completed") {
          clearInterval(interval)
          setStatus("completed")
          setResult(data)
        } else if (data.status === "failed") {
          clearInterval(interval)
          setStatus("error")
        }
        // If still "processing", continue polling
      } catch (error) {
        console.error("Polling error:", error)
        clearInterval(interval)
        setStatus("error")
      }
    }, 5000) // Poll every 5 seconds
    
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async ({ repoUrl, pdfPath, mode }: AuditSubmitData) => {
    setStatus("processing")
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/audit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: repoUrl,
          pdf_path: pdfPath,
          mode: mode
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || "Failed to submit audit")
      }
      
      const submitResult = await response.json()
      setAuditId(submitResult.audit_id)
      
      // Start polling for results
      pollForResults(submitResult.audit_id)
    } catch (error) {
      console.error("Submission error:", error)
      setStatus("error")
    }
  }

  const handleNewAudit = () => {
    setAuditId(null)
    setResult(null)
    setStatus("idle")
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            ⚖️ Automaton Auditor Swarm
          </h1>
          <p className="text-xl text-slate-300">
            Autonomous code auditing with LangGraph multi-agent architecture
          </p>
        </header>

        {status === "idle" || status === "error" ? (
          <AuditForm 
            onSubmit={handleSubmit} 
            error={status === "error"} 
            onRetry={handleNewAudit}
          />
        ) : status === "processing" ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mx-auto mb-6"></div>
            <h2 className="text-2xl font-semibold text-white mb-2">Running Audit...</h2>
            <p className="text-slate-400">Analyzing repository with Detective + Judicial layers</p>
            {auditId && (
              <p className="text-sm text-slate-500 mt-4">Audit ID: <code className="bg-slate-800 px-2 py-1 rounded">{auditId}</code></p>
            )}
          </div>
        ) : result ? (
          <ResultsViewer 
            result={result} 
            onNewAudit={handleNewAudit} 
          />
        ) : (
          <div className="text-center py-20">
            <p className="text-white">Loading results...</p>
          </div>
        )}
      </div>
    </main>
  )
}