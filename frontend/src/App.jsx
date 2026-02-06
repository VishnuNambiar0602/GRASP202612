import { useState } from 'react'
import axios from 'axios'

const URGENCY_CONFIG = {
  1: {
    label: 'LIFE-THREATENING',
    color: 'bg-red-600',
    textColor: 'text-white',
    borderColor: 'border-red-700',
    icon: '🚨'
  },
  2: {
    label: 'EMERGENCY',
    color: 'bg-orange-500',
    textColor: 'text-white',
    borderColor: 'border-orange-600',
    icon: '⚠️'
  },
  3: {
    label: 'URGENT',
    color: 'bg-yellow-500',
    textColor: 'text-gray-900',
    borderColor: 'border-yellow-600',
    icon: '⚡'
  },
  4: {
    label: 'SEMI-URGENT',
    color: 'bg-blue-500',
    textColor: 'text-white',
    borderColor: 'border-blue-600',
    icon: 'ℹ️'
  },
  5: {
    label: 'NON-URGENT',
    color: 'bg-green-500',
    textColor: 'text-white',
    borderColor: 'border-green-600',
    icon: '✓'
  }
}

function App() {
  const [symptoms, setSymptoms] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleTriage = async () => {
    if (!symptoms.trim()) {
      alert('Please enter patient symptoms')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post('http://localhost:8000/triage', {
        text_description: symptoms
      })
      
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to triage API. Is the backend running?')
      console.error('Triage error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getUrgencyConfig = (level) => URGENCY_CONFIG[level] || URGENCY_CONFIG[3]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-2">
            🏥 TriageFlow
          </h1>
          <p className="text-lg text-gray-600">
            AI-Powered Medical Triage System
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Reasoning-First • Chain-of-Thought Analysis • Safety-Critical Design
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Patient Symptom Description
          </label>
          <textarea
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            placeholder="Enter detailed patient symptoms here... (e.g., 'Patient reports severe chest pain radiating to left arm, difficulty breathing, sweating profusely')"
            className="w-full h-40 px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-gray-800"
            disabled={loading}
          />
          
          <button
            onClick={handleTriage}
            disabled={loading || !symptoms.trim()}
            className={`mt-4 w-full py-4 rounded-lg font-bold text-lg transition-all duration-200 ${
              loading || !symptoms.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-xl transform hover:scale-[1.02]'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analyzing Symptoms...
              </span>
            ) : (
              '🔍 Run Triage Analysis'
            )}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-800 font-semibold">⚠️ Error</p>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-6">
            {/* Ambulance Dispatch Alert */}
            {result.dispatch_ambulance && (
              <div className="bg-red-600 border-4 border-red-800 rounded-lg p-6 animate-flash">
                <div className="flex items-center justify-center gap-4">
                  <span className="text-6xl">🚑</span>
                  <div>
                    <p className="text-white text-2xl font-bold">
                      AMBULANCE DISPATCH ACTIVATED
                    </p>
                    <p className="text-red-100 text-sm mt-1">
                      MATS Emergency Protocol Initiated • Immediate Medical Response Required
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Urgency Level Card */}
            <div className={`rounded-lg shadow-xl p-6 border-4 ${getUrgencyConfig(result.urgency_level).borderColor} ${getUrgencyConfig(result.urgency_level).color}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-6xl">{getUrgencyConfig(result.urgency_level).icon}</span>
                  <div>
                    <p className={`text-sm font-semibold ${getUrgencyConfig(result.urgency_level).textColor} opacity-90`}>
                      Triage Classification
                    </p>
                    <h2 className={`text-3xl font-bold ${getUrgencyConfig(result.urgency_level).textColor}`}>
                      Level {result.urgency_level}: {getUrgencyConfig(result.urgency_level).label}
                    </h2>
                  </div>
                </div>
                
                {/* Uncertainty Score */}
                <div className="text-right">
                  <p className={`text-sm font-semibold ${getUrgencyConfig(result.urgency_level).textColor} opacity-90`}>
                    Uncertainty Score
                  </p>
                  <p className={`text-2xl font-bold ${getUrgencyConfig(result.urgency_level).textColor}`}>
                    {(result.uncertainty_score * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Safety Flag */}
              {result.safety_flag && (
                <div className="mt-4 bg-white/20 backdrop-blur-sm rounded-lg p-3 border-2 border-white/30">
                  <p className={`text-sm font-bold ${getUrgencyConfig(result.urgency_level).textColor}`}>
                    ⚠️ SAFETY FLAG: High uncertainty detected - Recommend manual clinical review
                  </p>
                </div>
              )}
            </div>

            {/* Reasoning Trace Section */}
            <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-600">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🧠</span>
                <h3 className="text-2xl font-bold text-gray-900">
                  Chain-of-Thought Reasoning Trace
                </h3>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800 leading-relaxed">
                  {result.clinical_reasoning}
                </pre>
              </div>

              {/* Metadata */}
              <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
                <span>Timestamp: {new Date(result.timestamp).toLocaleString()}</span>
                <span>Model: Gemini 1.5 Flash • TriageFlow v1.0</span>
              </div>
            </div>

            {/* Clear Button */}
            <button
              onClick={() => {
                setResult(null)
                setSymptoms('')
              }}
              className="w-full py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors"
            >
              Clear & New Analysis
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
