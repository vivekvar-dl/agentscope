'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Download, Activity, Clock, DollarSign, Cpu, AlertCircle } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface ExecutionStep {
  timestamp: string
  type: string
  content: string
  tokens: number
  cost: number
  duration_ms: number
  metadata?: Record<string, any>
}

interface Metrics {
  status: string
  duration_seconds: number
  total_tokens: number
  total_cost: number
  tool_calls: number
  decisions: number
  steps: ExecutionStep[]
}

export default function Home() {
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo')
  const [task, setTask] = useState('Research the latest developments in AI agents and provide a comprehensive summary')
  const [isRunning, setIsRunning] = useState(false)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [steps, setSteps] = useState<ExecutionStep[]>([])
  const [ws, setWs] = useState<WebSocket | null>(null)

  const models = [
    { id: 'gpt-4', name: 'GPT-4', cost: '$0.03/1K' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', cost: '$0.0005/1K' },
    { id: 'claude-3-opus', name: 'Claude 3 Opus', cost: '$0.015/1K' },
    { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', cost: '$0.003/1K' },
    { id: 'gemini-pro', name: 'Gemini Pro', cost: '$0.0005/1K' },
  ]

  const executeAgent = async () => {
    setIsRunning(true)
    setSteps([])
    setMetrics(null)

    // Create WebSocket connection
    const websocket = new WebSocket('ws://localhost:8000/ws/execute')
    
    websocket.onopen = () => {
      websocket.send(JSON.stringify({
        model: selectedModel,
        task: task,
        max_tokens: 2000,
        temperature: 0.7,
        tools: []
      }))
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'step') {
        setSteps(prev => [...prev, data.step])
      } else if (data.type === 'completed') {
        setMetrics(data.metrics)
        setIsRunning(false)
        websocket.close()
      } else if (data.type === 'error') {
        console.error(data.message)
        setIsRunning(false)
        websocket.close()
      }
    }

    setWs(websocket)
  }

  const exportTrace = () => {
    if (!metrics) return
    
    const trace = {
      timestamp: new Date().toISOString(),
      model: selectedModel,
      task: task,
      metrics: metrics
    }
    
    const blob = new Blob([JSON.stringify(trace, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `agentscope-trace-${Date.now()}.json`
    a.click()
  }

  const chartData = steps.map((step, i) => ({
    name: `Step ${i + 1}`,
    tokens: step.tokens,
    cost: step.cost * 1000, // Convert to $/1K tokens
  }))

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-blue-800/50 backdrop-blur-sm bg-gray-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                🔍 AgentScope
              </h1>
              <p className="text-gray-400 mt-1">Real-time AI Agent Monitoring</p>
            </div>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/vivekvar-dl/agentscope"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                ⭐ Star on GitHub
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Configuration */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            {/* Config Card */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Agent Configuration
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {models.map(model => (
                      <option key={model.id} value={model.id}>
                        {model.name} ({model.cost})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Agent Task
                  </label>
                  <textarea
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    rows={4}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your agent's task..."
                  />
                </div>

                <button
                  onClick={executeAgent}
                  disabled={isRunning}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed rounded-lg px-6 py-3 font-semibold flex items-center justify-center gap-2 transition-all"
                >
                  {isRunning ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      Execute Agent
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Metrics Cards */}
            {metrics && (
              <div className="grid grid-cols-2 gap-4">
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-gradient-to-br from-blue-600/20 to-cyan-600/20 backdrop-blur-sm rounded-xl border border-blue-500/50 p-4"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/20 rounded-lg">
                      <Clock className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Duration</p>
                      <p className="text-2xl font-bold">{metrics.duration_seconds.toFixed(2)}s</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 }}
                  className="bg-gradient-to-br from-green-600/20 to-emerald-600/20 backdrop-blur-sm rounded-xl border border-green-500/50 p-4"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-500/20 rounded-lg">
                      <DollarSign className="w-5 h-5 text-green-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Cost</p>
                      <p className="text-2xl font-bold">${metrics.total_cost.toFixed(4)}</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-sm rounded-xl border border-purple-500/50 p-4"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-500/20 rounded-lg">
                      <Cpu className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Tokens</p>
                      <p className="text-2xl font-bold">{metrics.total_tokens}</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className="bg-gradient-to-br from-orange-600/20 to-red-600/20 backdrop-blur-sm rounded-xl border border-orange-500/50 p-4"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-500/20 rounded-lg">
                      <Activity className="w-5 h-5 text-orange-400" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Tool Calls</p>
                      <p className="text-2xl font-bold">{metrics.tool_calls}</p>
                    </div>
                  </div>
                </motion.div>
              </div>
            )}

            {/* Charts */}
            {chartData.length > 0 && (
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
                <h3 className="text-lg font-semibold mb-4">Token Usage by Step</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem' }}
                    />
                    <Bar dataKey="tokens" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </motion.div>

          {/* Right Column - Execution Log */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  📝 Execution Log
                </h2>
                {metrics && (
                  <button
                    onClick={exportTrace}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Export
                  </button>
                )}
              </div>

              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {steps.length === 0 && !isRunning && (
                  <div className="text-center py-12 text-gray-500">
                    <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No execution yet. Click "Execute Agent" to start.</p>
                  </div>
                )}

                {steps.map((step, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`
                        p-2 rounded-lg mt-0.5
                        ${step.type === 'thought' ? 'bg-blue-500/20' : ''}
                        ${step.type === 'tool_call' ? 'bg-green-500/20' : ''}
                        ${step.type === 'decision' ? 'bg-purple-500/20' : ''}
                      `}>
                        {step.type === 'thought' && '💭'}
                        {step.type === 'tool_call' && '🔧'}
                        {step.type === 'decision' && '🎯'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-gray-300">
                            {step.type.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">
                            {step.duration_ms}ms
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 break-words">{step.content}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>{step.tokens} tokens</span>
                          <span>${step.cost.toFixed(4)}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}

                {isRunning && steps.length === 0 && (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-gray-400">Initializing agent...</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
