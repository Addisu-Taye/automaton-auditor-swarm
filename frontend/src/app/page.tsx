"use client"

import { useState, useCallback, useEffect } from "react"
import { AuditForm, type AuditSubmitData } from "@/components/AuditForm"
import { ResultsViewer, type AuditResult } from "@/components/ResultsViewer"
import { AlertCircle } from "lucide-react"

// API Base URL - loaded from environment with fallback
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"

export default function Home() {
  const [auditId, setAuditId] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "processing" | "completed" | "error">("idle")
  const [result, setResult] = useState<AuditResult | null>(null)
  const [errorDetails, setErrorDetails] = useState<string>("")

  // Poll for audit results
  const pollForResults = useCallback(async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/audit/${id}`)
        const data = await response.json()
        
        if (data.status === "completed") {
          clearInterval(interval)
          setStatus("completed")
          
          // Map API response to AuditResult type
          const mappedResult: AuditResult = {
            audit_id: data.audit_id,
            overall_score: data.final_report?.overall_score ?? data.overall_score ?? 0,
            criteria_evaluated: data.final_report?.criteria_evaluated ?? data.criteria_evaluated ?? 0,
            executive_summary: data.final_report?.executive_summary ?? data.executive_summary ?? "",
            criteria: data.final_report?.criteria ?? data.criteria ?? [],
            remediation_plan: data.final_report?.remediation_plan ?? data.remediation_plan ?? "",
            report_markdown: data.report_markdown ?? ""
          }
          
          setResult(mappedResult)
        } else if (data.status === "failed") {
          clearInterval(interval)
          setStatus("error")
          setErrorDetails(data.detail || "Audit failed")
        }
        // If still "processing", continue polling
      } catch (error) {
        console.error("Polling error:", error)
        clearInterval(interval)
        setStatus("error")
        setErrorDetails(error instanceof Error ? error.message : "Polling failed")
      }
    }, 5000) // Poll every 5 seconds
    
    return () => clearInterval(interval)
  }, [])

  // Handle form submission
  const handleSubmit = useCallback(async (data: AuditSubmitData) => {
    setStatus("processing")
    setErrorDetails("")
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/audit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: data.repoUrl,
          pdf_path: data.pdfPath,
          mode: data.mode
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
      setErrorDetails(error instanceof Error ? error.message : "Unknown error")
    }
  }, [pollForResults])

  // Handle new audit (reset state)
  const handleNewAudit = useCallback(() => {
    setAuditId(null)
    setResult(null)
    setErrorDetails("")
    setStatus("idle")
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            ⚖️ Automaton Auditor Swarm
          </h1>
          <p className="text-xl text-slate-300">
            Autonomous code auditing with LangGraph multi-agent architecture
          </p>
        </header>

        {/* Content based on status */}
        {status === "idle" || status === "error" ? (
          <AuditForm 
            onSubmit={handleSubmit} 
            error={status === "error"} 
            errorDetails={errorDetails}
            onRetry={handleNewAudit}
          />
        ) : status === "processing" ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mx-auto mb-6"></div>
            <h2 className="text-2xl font-semibold text-white mb-2">Running Audit...</h2>
            <p className="text-slate-400">Analyzing repository with Detective + Judicial layers</p>
            {auditId && (
              <p className="text-sm text-slate-500 mt-4">
                Audit ID: <code className="bg-slate-800 px-2 py-1 rounded">{auditId}</code>
              </p>
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