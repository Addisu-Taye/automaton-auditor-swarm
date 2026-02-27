"use client"

import { useState } from "react"
import ReactMarkdown from "react-markdown"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  AlertCircle, 
  CheckCircle, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  RefreshCw, 
  Scale, 
  Shield, 
  TrendingUp,
  AlertTriangle,
  Copy,
  Download
} from "lucide-react"

// Type definitions for audit results
export type JudgeOpinion = {
  judge: "Prosecutor" | "Defense" | "TechLead"
  score: number
  argument: string
  cited_evidence?: string[]
}

export type CriterionResult = {
  dimension_id: string
  dimension_name: string
  final_score: number
  judge_opinions: JudgeOpinion[]
  dissent_summary?: string
  remediation: string
}

export type AuditResult = {
  audit_id: string
  overall_score: number
  criteria_evaluated: number
  executive_summary: string
  criteria: CriterionResult[]
  remediation_plan: string
  report_markdown: string
}

interface ResultsViewerProps {
  result: AuditResult
  onNewAudit: () => void
}

// Type guard to validate audit result
function isValidAuditResult(result: any): result is AuditResult {
  return (
    result &&
    typeof result.overall_score === "number" &&
    Array.isArray(result.criteria) &&
    typeof result.executive_summary === "string"
  )
}

export function ResultsViewer({ result, onNewAudit }: ResultsViewerProps) {
  const [expandedCriteria, setExpandedCriteria] = useState<Set<string>>(new Set())
  const [activeTab, setActiveTab] = useState<"summary" | "breakdown" | "report">("summary")

  // Validate result data
  if (!isValidAuditResult(result)) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="py-12 text-center">
          <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            Invalid Audit Result
          </h3>
          <p className="text-slate-400 mb-4">
            The audit result data is incomplete or malformed.
          </p>
          <Button onClick={onNewAudit} variant="default" className="bg-purple-600 hover:bg-purple-700">
            Start New Audit
          </Button>
        </CardContent>
      </Card>
    )
  }

  const toggleCriterion = (id: string) => {
    setExpandedCriteria(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const getScoreColor = (score: number): string => {
    if (score >= 5) return "text-green-500"
    if (score >= 4) return "text-emerald-500"
    if (score >= 3) return "text-yellow-500"
    if (score >= 2) return "text-orange-500"
    return "text-red-500"
  }

  const getScoreBadge = (score: number) => {
    if (score >= 5) return <Badge className="bg-green-600 hover:bg-green-700">Excellent</Badge>
    if (score >= 4) return <Badge className="bg-emerald-600 hover:bg-emerald-700">Good</Badge>
    if (score >= 3) return <Badge className="bg-yellow-600 hover:bg-yellow-700">Adequate</Badge>
    if (score >= 2) return <Badge className="bg-orange-600 hover:bg-orange-700">Needs Work</Badge>
    return <Badge className="bg-red-600 hover:bg-red-700">Critical</Badge>
  }

  const getJudgeIcon = (judge: string) => {
    switch (judge) {
      case "Prosecutor": return <AlertCircle className="h-4 w-4 text-red-500" />
      case "Defense": return <Shield className="h-4 w-4 text-green-500" />
      case "TechLead": return <TrendingUp className="h-4 w-4 text-blue-500" />
      default: return <Scale className="h-4 w-4 text-gray-500" />
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (err) {
      console.error("Failed to copy:", err)
    }
  }

  const downloadReport = () => {
    const blob = new Blob([result.report_markdown], { type: "text/markdown" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `audit-report-${result.audit_id.slice(0, 8)}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Safe score access with defaults
  const safeOverallScore = result.overall_score ?? 0
  const safeCriteriaEvaluated = result.criteria_evaluated ?? 0

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex flex-wrap gap-3 justify-between items-center">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono">
            ID: {result.audit_id.slice(0, 8)}...
          </Badge>
          <Badge variant="secondary">
            {safeCriteriaEvaluated} criteria evaluated
          </Badge>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => copyToClipboard(result.report_markdown)}
            className="gap-1"
          >
            <Copy className="h-4 w-4" />
            Copy
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={downloadReport}
            className="gap-1"
          >
            <Download className="h-4 w-4" />
            Download
          </Button>
          <Button 
            variant="default" 
            size="sm"
            onClick={onNewAudit}
            className="gap-1 bg-purple-600 hover:bg-purple-700"
          >
            <RefreshCw className="h-4 w-4" />
            New Audit
          </Button>
        </div>
      </div>

      {/* Score Overview Card */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader className="pb-4">
          <CardTitle className="text-white flex items-center gap-2">
            <Scale className="h-5 w-5 text-purple-400" />
            Audit Summary
          </CardTitle>
          <CardDescription className="text-slate-400">
            Overall assessment based on {safeCriteriaEvaluated} rubric dimensions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Overall Score */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">Overall Score</p>
              <p className={`text-3xl font-bold ${getScoreColor(safeOverallScore)}`}>
                {safeOverallScore.toFixed(2)}
                <span className="text-lg text-slate-500">/5.0</span>
              </p>
            </div>
            <div className="text-right">
              {getScoreBadge(Math.round(safeOverallScore))}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Quality Score</span>
              <span className="text-white font-medium">{Math.round(safeOverallScore * 20)}%</span>
            </div>
            <Progress 
              value={safeOverallScore * 20} 
              className="h-2 bg-slate-700"
            />
          </div>

          {/* Executive Summary */}
          <div className="pt-4 border-t border-slate-700">
            <h4 className="text-sm font-medium text-slate-300 mb-2">Executive Summary</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              {result.executive_summary}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Tabs: Summary / Breakdown / Full Report */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-slate-800">
          <TabsTrigger 
            value="summary" 
            className="data-[state=active]:bg-purple-600 data-[state=active]:text-white"
          >
            Summary
          </TabsTrigger>
          <TabsTrigger 
            value="breakdown"
            className="data-[state=active]:bg-purple-600 data-[state=active]:text-white"
          >
            Breakdown
          </TabsTrigger>
          <TabsTrigger 
            value="report"
            className="data-[state=active]:bg-purple-600 data-[state=active]:text-white"
          >
            Full Report
          </TabsTrigger>
        </TabsList>

        {/* Summary Tab */}
        <TabsContent value="summary" className="space-y-4 mt-4">
          {/* Key Findings */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg">Key Findings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {result.criteria.slice(0, 3).map((criterion) => (
                <div 
                  key={criterion.dimension_id}
                  className="flex items-start justify-between p-3 rounded-lg bg-slate-900/50"
                >
                  <div className="space-y-1">
                    <p className="font-medium text-white text-sm">
                      {criterion.dimension_name}
                    </p>
                    <p className="text-slate-400 text-xs line-clamp-2">
                      {criterion.remediation}
                    </p>
                  </div>
                  <Badge variant="outline" className={getScoreColor(criterion.final_score ?? 0)}>
                    {(criterion.final_score ?? 0)}/5
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Remediation Plan Preview */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                Priority Remediation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-invert prose-sm max-w-none bg-slate-900/50 p-4 rounded-lg overflow-x-auto text-slate-300">
  <ReactMarkdown
    components={{
      h1: ({ children }) => <h1 className="text-xl font-bold text-white mt-6 mb-3">{children}</h1>,
      h2: ({ children }) => <h2 className="text-lg font-semibold text-white mt-5 mb-2">{children}</h2>,
      h3: ({ children }) => <h3 className="text-base font-medium text-white mt-4 mb-2">{children}</h3>,
      p: ({ children }) => <p className="text-slate-300 my-2 leading-relaxed">{children}</p>,
      ul: ({ children }) => <ul className="list-disc list-inside text-slate-300 my-2 space-y-1">{children}</ul>,
      ol: ({ children }) => <ol className="list-decimal list-inside text-slate-300 my-2 space-y-1">{children}</ol>,
      li: ({ children }) => <li className="text-slate-300">{children}</li>,
      code: ({ children, className }) => (
        <code className={`bg-slate-800 px-1.5 py-0.5 rounded text-sm ${className || ''}`}>
          {children}
        </code>
      ),
      pre: ({ children }) => (
        <pre className="bg-slate-900 p-3 rounded-lg overflow-x-auto my-3">
          {children}
        </pre>
      ),
      blockquote: ({ children }) => (
        <blockquote className="border-l-4 border-purple-500 pl-4 italic text-slate-400 my-3">
          {children}
        </blockquote>
      ),
      a: ({ children, href }) => (
        <a 
          href={href} 
          className="text-purple-400 hover:text-purple-300 underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          {children}
        </a>
      ),
    }}
  >
    {result.report_markdown}
  </ReactMarkdown>
</div>
              <Button 
                variant="link" 
                className="text-purple-400 p-0 h-auto mt-2"
                onClick={() => setActiveTab("breakdown")}
              >
                View full remediation plan →
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Breakdown Tab */}
        <TabsContent value="breakdown" className="mt-4">
          <div className="space-y-4">
            {result.criteria.map((criterion) => {
              const isExpanded = expandedCriteria.has(criterion.dimension_id)
              return (
                <Card 
                  key={criterion.dimension_id}
                  className="bg-slate-800/50 border-slate-700 overflow-hidden"
                >
                  <button
                    onClick={() => toggleCriterion(criterion.dimension_id)}
                    className="w-full p-4 flex items-center justify-between hover:bg-slate-700/50 transition-colors text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${getScoreColor(criterion.final_score ?? 0)}`} />
                      <div>
                        <h4 className="font-medium text-white">
                          {criterion.dimension_name}
                        </h4>
                        <p className="text-xs text-slate-400">
                          {criterion.judge_opinions?.length ?? 0} judge opinions
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className={getScoreColor(criterion.final_score ?? 0)}>
                        {(criterion.final_score ?? 0)}/5
                      </Badge>
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-slate-400" />
                      )}
                    </div>
                  </button>

                  {isExpanded && (
                    <CardContent className="pt-0 pb-4 space-y-4 border-t border-slate-700 mt-2">
                      {/* Judge Opinions */}
                      <div className="space-y-3">
                        <h5 className="text-sm font-medium text-slate-300">Judge Opinions</h5>
                        {(criterion.judge_opinions || []).map((opinion, idx) => (
                          <div 
                            key={idx}
                            className="p-3 rounded-lg bg-slate-900/50 space-y-2"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                {getJudgeIcon(opinion.judge)}
                                <span className="font-medium text-white text-sm">
                                  {opinion.judge}
                                </span>
                              </div>
                              <Badge variant="secondary" className="text-xs">
                                Score: {(opinion.score ?? 0)}/5
                              </Badge>
                            </div>
                            <p className="text-slate-400 text-sm leading-relaxed">
                              {opinion.argument}
                            </p>
                            {opinion.cited_evidence && opinion.cited_evidence.length > 0 && (
                              <div className="pt-2 border-t border-slate-700">
                                <p className="text-xs text-slate-500 mb-1">Cited Evidence:</p>
                                <div className="flex flex-wrap gap-1">
                                  {opinion.cited_evidence.slice(0, 3).map((evidence, i) => (
                                    <code 
                                      key={i}
                                      className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300"
                                    >
                                      {evidence}
                                    </code>
                                  ))}
                                  {opinion.cited_evidence.length > 3 && (
                                    <span className="text-xs text-slate-500">
                                      +{opinion.cited_evidence.length - 3} more
                                    </span>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>

                      {/* Dissent Summary */}
                      {criterion.dissent_summary && (
                        <div className="p-3 rounded-lg bg-yellow-900/20 border border-yellow-700/50">
                          <div className="flex items-start gap-2">
                            <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-sm font-medium text-yellow-200">
                                Dissent Detected
                              </p>
                              <p className="text-xs text-yellow-100/80 mt-1">
                                {criterion.dissent_summary}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Remediation */}
                      <div className="p-3 rounded-lg bg-blue-900/20 border border-blue-700/50">
                        <p className="text-sm font-medium text-blue-200 mb-1">
                          Remediation
                        </p>
                        <p className="text-xs text-blue-100/80">
                          {criterion.remediation}
                        </p>
                      </div>
                    </CardContent>
                  )}
                </Card>
              )
            })}
          </div>
        </TabsContent>

        {/* Full Report Tab */}
        <TabsContent value="report" className="mt-4">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-white">Full Audit Report</CardTitle>
                <CardDescription className="text-slate-400">
                  Complete markdown report with all findings and recommendations
                </CardDescription>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={downloadReport}
                className="gap-1"
              >
                <Download className="h-4 w-4" />
                Download .md
              </Button>
            </CardHeader>
            <CardContent>
              <div className="prose prose-invert prose-sm max-w-none bg-slate-900/50 p-4 rounded-lg overflow-x-auto">
                <ReactMarkdown
                  components={{
                    h1: ({ children }) => <h1 className="text-xl font-bold text-white mt-6 mb-3">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-lg font-semibold text-white mt-5 mb-2">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-base font-medium text-white mt-4 mb-2">{children}</h3>,
                    p: ({ children }) => <p className="text-slate-300 my-2 leading-relaxed">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside text-slate-300 my-2 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside text-slate-300 my-2 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="text-slate-300">{children}</li>,
                    code: ({ children, className }) => (
                      <code className={`bg-slate-800 px-1.5 py-0.5 rounded text-sm ${className || ''}`}>
                        {children}
                      </code>
                    ),
                    pre: ({ children }) => (
                      <pre className="bg-slate-900 p-3 rounded-lg overflow-x-auto my-3">
                        {children}
                      </pre>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-purple-500 pl-4 italic text-slate-400 my-3">
                        {children}
                      </blockquote>
                    ),
                    a: ({ children, href }) => (
                      <a 
                        href={href} 
                        className="text-purple-400 hover:text-purple-300 underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {children}
                      </a>
                    ),
                  }}
                >
                  {result.report_markdown}
                </ReactMarkdown>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer Actions */}
      <div className="flex justify-center pt-6">
        <Button 
          variant="outline"
          onClick={onNewAudit}
          className="gap-2 border-slate-600 text-slate-300 hover:bg-slate-700"
        >
          <RefreshCw className="h-4 w-4" />
          Start New Audit
        </Button>
      </div>
    </div>
  )
}