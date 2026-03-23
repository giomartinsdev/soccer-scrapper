import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [predictions, setPredictions] = useState([])
  const [events, setEvents] = useState([])
  const [allEvents, setAllEvents] = useState([])
  const [live, setLive] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('predictions')
  const [showAllEvents, setShowAllEvents] = useState(false)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [predictionsRes, eventsRes, liveRes, allEventsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/predictions?limit=20`),
        axios.get(`${API_BASE}/api/v1/events?limit=20`),
        axios.get(`${API_BASE}/api/v1/live?limit=20`),
        axios.get(`${API_BASE}/api/v1/events?limit=50`)
      ])
      setPredictions(predictionsRes.data.items || [])
      setEvents(eventsRes.data.items || [])
      setLive(liveRes.data.items || [])
      setAllEvents(allEventsRes.data.items || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching data:', err)
      setError('Failed to fetch data. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const getPredictionBadge = (pred) => {
    const badge = pred.predicted_result === 'H' ? { label: 'Home', class: 'bg-green-500/20 text-green-400' }
      : pred.predicted_result === 'A' ? { label: 'Away', class: 'bg-red-500/20 text-red-400' }
      : { label: 'Draw', class: 'bg-yellow-500/20 text-yellow-400' }
    return badge
  }

  const formatConfidence = (conf) => {
    return Math.round(conf || 0)
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'TBD'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const getStatusBadge = (status) => {
    if (!status) return null
    const statusLower = status.toLowerCase()
    if (statusLower === 'notstarted' || statusLower === 'finished') return null
    return { label: status, class: 'bg-green-500/20 text-green-400' }
  }

  const getFinishedBadge = (status) => {
    if (!status) return null
    const statusLower = status.toLowerCase()
    if (statusLower === 'finished') return { label: 'Finished', class: 'bg-slate-500/20 text-slate-400' }
    return null
  }

  if (loading && predictions.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-700 border-t-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center p-8 bg-slate-800 rounded-xl">
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={fetchData} className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
            Retry
          </button>
        </div>
      </div>
    )
  }

  const sortedPredictions = [...predictions]
    .filter(p => p.event?.home_team)
    .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
    .slice(0, 10)

  const upcomingEvents = [...events]
    .filter(e => e.home_team && (!e.status || e.status === 'notstarted'))
    .slice(0, 10)

  const displayEvents = showAllEvents ? allEvents.filter(e => e.home_team) : upcomingEvents

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <span className="text-3xl">⚽</span>
              Soccer Scrapper
            </h1>
            <button
              onClick={fetchData}
              className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </header>

      {live.length > 0 && (
        <div className="bg-green-900/30 border-b border-green-800">
          <div className="max-w-6xl mx-auto px-4 py-3">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-green-400 font-semibold text-sm">LIVE NOW</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              {live.slice(0, 3).map((item, idx) => (
                <div key={idx} className="bg-slate-800 rounded-lg p-3 flex items-center justify-between">
                  <div>
                    <span className="text-white font-medium">{item.home_team || 'TBD'}</span>
                    <span className="text-slate-500 mx-2">vs</span>
                    <span className="text-white font-medium">{item.away_team || 'TBD'}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-bold text-green-400">
                      {item.home_score ?? 0}-{item.away_score ?? 0}
                    </span>
                    <span className="text-yellow-400 text-sm ml-2">{item.current_minute}'</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('predictions')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'predictions'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Top Predictions
          </button>
          <button
            onClick={() => setActiveTab('events')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'events'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Events
          </button>
        </div>

        {activeTab === 'predictions' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {sortedPredictions.map((pred, idx) => {
                const badge = getPredictionBadge(pred)
                return (
                  <div key={idx} className="bg-slate-800 rounded-xl p-5 border-l-4 border-blue-500">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="text-slate-400 text-sm mb-1">{pred.event?.league?.name || 'Unknown League'}</div>
                        <div className="text-xl font-bold text-white">
                          {pred.event?.home_team || 'Home'} vs {pred.event?.away_team || 'Away'}
                        </div>
                        <div className="text-slate-500 text-sm mt-1">
                          {formatDate(pred.event?.event_date)}
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${badge.class}`}>
                        {badge.label} ({pred.predicted_result})
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Confidence</span>
                        <span className="text-white font-medium">{formatConfidence(pred.confidence)}%</span>
                      </div>
                      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full transition-all duration-500"
                          style={{ width: `${formatConfidence(pred.confidence)}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                      <div className="bg-slate-700/50 rounded-lg p-2">
                        <div className="text-slate-400 text-xs mb-1">Expected Score</div>
                        <div className="text-white font-bold">{pred.most_likely_score || 'N/A'}</div>
                      </div>
                      <div className="bg-slate-700/50 rounded-lg p-2">
                        <div className="text-slate-400 text-xs mb-1">Over 2.5</div>
                        <div className="text-white font-bold">{Math.round(pred.prob_over_25 || 0)}%</div>
                      </div>
                      <div className="bg-slate-700/50 rounded-lg p-2">
                        <div className="text-slate-400 text-xs mb-1">BTTS</div>
                        <div className="text-white font-bold">{Math.round(pred.prob_btts_yes || 0)}%</div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
            
            {sortedPredictions.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                No predictions available. Run a scraping job to get predictions.
              </div>
            )}
          </div>
        )}

        {activeTab === 'events' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">
                {showAllEvents ? `Last ${displayEvents.length} Events` : 'Upcoming Matches'}
              </h2>
              <button
                onClick={() => setShowAllEvents(!showAllEvents)}
                className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 text-sm"
              >
                {showAllEvents ? 'Show Upcoming Only' : 'Show Last 50 Events'}
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {displayEvents.map((event, idx) => {
                const statusBadge = getStatusBadge(event.status)
                const finishedBadge = getFinishedBadge(event.status)
                return (
                  <div key={idx} className={`bg-slate-800 rounded-xl p-4 border-l-4 ${finishedBadge ? 'border-slate-500' : 'border-green-500'}`}>
                    <div className="text-slate-400 text-sm mb-2">{event.league?.name || 'Unknown League'}</div>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="text-white font-medium">{event.home_team || 'TBD'}</div>
                        <div className="text-slate-500 text-sm">vs</div>
                        <div className="text-white font-medium">{event.away_team || 'TBD'}</div>
                      </div>
                      <div className="text-right">
                        {event.home_score !== null && (
                          <div className="text-2xl font-bold text-white">
                            {event.home_score} - {event.away_score}
                          </div>
                        )}
                        {statusBadge && (
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${statusBadge.class}`}>
                            {statusBadge.label}
                          </span>
                        )}
                        {finishedBadge && (
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${finishedBadge.class}`}>
                            {finishedBadge.label}
                          </span>
                        )}
                        {event.current_minute && (
                          <div className="text-yellow-400 text-sm mt-1">{event.current_minute}'</div>
                        )}
                        {!statusBadge && !finishedBadge && !event.current_minute && event.event_date && (
                          <div className="text-slate-500 text-sm mt-1">
                            {formatDate(event.event_date)}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {(event.odds_home || event.odds_draw || event.odds_away) && (
                      <div className="mt-3 pt-3 border-t border-slate-700 grid grid-cols-3 gap-2 text-center">
                        <div className="bg-slate-700/30 rounded p-2">
                          <div className="text-slate-500 text-xs">Home</div>
                          <div className="text-white font-bold">{event.odds_home?.toFixed(2) || '-'}</div>
                        </div>
                        <div className="bg-slate-700/30 rounded p-2">
                          <div className="text-slate-500 text-xs">Draw</div>
                          <div className="text-white font-bold">{event.odds_draw?.toFixed(2) || '-'}</div>
                        </div>
                        <div className="bg-slate-700/30 rounded p-2">
                          <div className="text-slate-500 text-xs">Away</div>
                          <div className="text-white font-bold">{event.odds_away?.toFixed(2) || '-'}</div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
            
            {displayEvents.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                No events available.
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center text-slate-500 text-sm">
          Soccer Scrapper - Auto-updating every minute
        </div>
      </footer>
    </div>
  )
}

export default App
