import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

const defaultQuestions = [
  {
    id: 1,
    type: 'theoretical',
    category: 'Frontend',
    level: 1,
    text: 'Explain the difference between props and state in React and when you would use each.',
    acceptedKeywords: ['props', 'state', 'props are', 'state is', 'immutable', 'component'],
  },
  {
    id: 7,
    type: 'coding',
    category: 'Frontend',
    level: 7,
    text: 'Write a function to flatten a nested array by one level in JavaScript.',
    starterCode: `function flattenOnce(arr) {
  // implement
}

console.log(flattenOnce([1, [2, 3], [4, [5]]]));
`,
    compiler: 'JavaScript',
    expectedOutput: '1 2 3 4',
  },
  {
    id: 8,
    type: 'theoretical',
    category: 'DevOps',
    level: 8,
    text: 'Explain the CI/CD pipeline and why automated testing is important in deployment.',
    acceptedKeywords: ['ci', 'cd', 'pipeline', 'testing', 'automated', 'deploy'],
  },
  {
    id: 9,
    type: 'coding',
    category: 'Algorithms',
    level: 9,
    text: 'Write a function that returns the nth Fibonacci number efficiently.',
    starterCode: `function fib(n) {
  // implement
}

console.log(fib(7));
`,
    compiler: 'JavaScript',
    expectedOutput: '13',
  },
  {
    id: 10,
    type: 'theoretical',
    category: 'Security',
    level: 10,
    text: 'What is XSS and how do you prevent it in web applications?',
    acceptedKeywords: ['xss', 'sanitize', 'escape', 'input', 'content security policy'],
  },
  {
    id: 11,
    type: 'theoretical',
    category: 'ML',
    level: 11,
    text: 'Describe the difference between supervised and unsupervised learning.',
    acceptedKeywords: ['supervised', 'unsupervised', 'labels', 'clustering', 'regression', 'classification'],
  },
  {
    id: 12,
    type: 'coding',
    category: 'Data',
    level: 12,
    text: 'Given an array of integers, return the index of the first repeated value.',
    starterCode: `function firstRepeatedIndex(arr) {
  // implement
}

console.log(firstRepeatedIndex([2,5,1,2,3,5]));
`,
    compiler: 'JavaScript',
    expectedOutput: '0',
  },
  {
    id: 2,
    type: 'coding',
    category: 'Frontend',
    level: 2,
    text: 'Write a JavaScript function that reverses a string without using the reverse() method.',
    starterCode: `function reverseString(str) {
  // write your logic here
}

console.log(reverseString('hello'));
`,
    compiler: 'JavaScript',
    expectedOutput: 'olleh',
  },
  {
    id: 3,
    type: 'theoretical',
    category: 'Backend',
    level: 3,
    text: 'How would you design a REST API endpoint for user login with security best practices?',
    acceptedKeywords: ['rest', 'endpoint', 'authentication', 'token', 'https', 'validation', 'rate limit'],
  },
  {
    id: 4,
    type: 'coding',
    category: 'Backend',
    level: 4,
    text: 'Write a function to check whether a number is prime in JavaScript.',
    starterCode: `function isPrime(num) {
  // implement prime check
}

console.log(isPrime(17));
`,
    compiler: 'JavaScript',
    expectedOutput: 'true',
  },
  {
    id: 5,
    type: 'theoretical',
    category: 'Database',
    level: 5,
    text: 'Compare relational and distributed data modeling. How would you choose a schema for a system with 10M events per day?',
    acceptedKeywords: ['relational', 'denormal', 'shard', 'partition', 'schema', 'normalization', 'denormalization'],
  },
  {
    id: 6,
    type: 'theoretical',
    category: 'System Design',
    level: 6,
    text: 'Design a scalable interview evaluation platform that captures live speech, stores answers, scores them, and serves actionable analytics in real time.',
    acceptedKeywords: ['scale', 'stream', 'real time', 'kafka', 'storage', 'analytics', 'pipeline'],
  },
]

const categories = ['All', 'Frontend', 'Backend', 'Database', 'System Design']

function App() {
  const [user, setUser] = useState({ name: 'Student', role: 'Student', email: 'student@example.com', password: '' })
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [questions, setQuestions] = useState(defaultQuestions)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [timer, setTimer] = useState(180)
  const [interviewStarted, setInterviewStarted] = useState(false)
  const [showIntro, setShowIntro] = useState(false)
  const [micPermission, setMicPermission] = useState('unknown') // 'unknown' | 'granted' | 'denied'
  const [micSupported, setMicSupported] = useState(false)
  const [report, setReport] = useState(null)
  const [codeOutput, setCodeOutput] = useState('')
  const [language, setLanguage] = useState('JavaScript')
  const [isListening, setIsListening] = useState(false)
  const [voiceError, setVoiceError] = useState('')
  const recognitionRef = useRef(null)
  const [newQuestion, setNewQuestion] = useState({
    category: 'Frontend',
    text: '',
    type: 'theoretical',
  })
  const [viewingAllQuestions, setViewingAllQuestions] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('All')

  const questionTypeOptions = ['theoretical', 'coding']
  const categories = ['All', 'Frontend', 'Backend', 'Database', 'System Design', 'DevOps', 'Security', 'ML', 'Algorithms', 'Data']

  const stopwords = new Set(['the','is','a','an','and','or','of','in','to','for','on','with','that','this','it','as','are'])

  const tokenize = (text) => {
    if (!text) return []
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(Boolean)
      .filter((w) => !stopwords.has(w))
  }

  const jaccardSimilarity = (aText, bText) => {
    const a = new Set(tokenize(aText))
    const b = new Set(tokenize(bText))
    const inter = [...a].filter((x) => b.has(x)).length
    const union = new Set([...a, ...b]).size
    return union === 0 ? 0 : inter / union
  }

  const filteredQuestions = useMemo(() => questions, [questions])

  const currentQuestion = filteredQuestions[currentIndex] ?? null
  const currentDifficultyLevel = currentQuestion?.level ?? currentIndex + 1
  const isAdmin = user.role === 'Admin'

  const startInterviewSession = () => {
    setTimer(180)
    setReport(null)
    setCodeOutput('')
    // Request mic permission at the moment interview starts (user gesture)
    requestMicrophonePermission().then(() => {
      setInterviewStarted(true)
    })
  }


  useEffect(() => {
    if (!showIntro || !isLoggedIn || report) return undefined

    const introText = `Hello ${user.name}. Welcome to your AI mock interview. I will ask a series of technical questions. Please answer clearly and confidently.`

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(introText)
      utterance.rate = 0.95
      utterance.pitch = 1
      utterance.lang = 'en-US'
      window.speechSynthesis.speak(utterance)
    }

    // Do not auto-start the interview; wait for the student to press Start Interview.
    return undefined
  }, [showIntro, isLoggedIn, report, user.name])

  useEffect(() => {
    if (!interviewStarted || report) return undefined

    const interval = setInterval(() => {
      setTimer((previousTimer) => {
        if (previousTimer <= 1) {
          clearInterval(interval)
          finishInterview(true)
          return 0
        }

        return previousTimer - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [interviewStarted, report])

  useEffect(() => {
    // Only present/read questions after the user is logged in, the interview has started,
    // and microphone permission is granted (for automatic voice capture).
    if (!currentQuestion || !isLoggedIn || !interviewStarted) return
    setCodeOutput('')
    setLanguage(currentQuestion.compiler ?? 'JavaScript')
    setVoiceError('')

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(currentQuestion.text)
      utterance.rate = 1
      utterance.pitch = 1
      utterance.lang = 'en-US'
      window.speechSynthesis.speak(utterance)
    }

    if (currentQuestion.type === 'theoretical') {
      // Only auto-start recognition when mic permission is granted
      if ((micPermission === 'granted') && (window.SpeechRecognition || window.webkitSpeechRecognition)) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        const recognition = new SpeechRecognition()
        recognition.lang = 'en-US'
        recognition.continuous = false
        recognition.interimResults = false

        recognition.onstart = () => {
          setVoiceError('')
          setIsListening(true)
        }

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript
          const existingText = answers[currentQuestion.id] ?? ''
          const nextValue = existingText ? `${existingText}\n${transcript}` : transcript
          handleAnswerChange(nextValue)
        }

        recognition.onerror = (event) => {
          const message = event.error === 'not-allowed'
            ? 'Microphone permission is blocked. Please allow microphone access and try again.'
            : 'Unable to capture speech. Please try again.'
          setVoiceError(message)
          setIsListening(false)
        }

        recognition.onend = () => {
          setIsListening(false)
        }

        recognitionRef.current = recognition
        window.setTimeout(() => {
          try {
            recognition.start()
          } catch {
            setVoiceError('Microphone is busy. Please try again in a moment.')
          }
        }, 600)
      } else {
        // If permission not granted, indicate that user can allow mic
        if (micPermission === 'denied') setVoiceError('Microphone permission denied. Please allow microphone to use voice answers.')
      }
    }
  }, [currentQuestion, isLoggedIn, interviewStarted, micPermission])

  const handleLogin = (event) => {
    event.preventDefault()

    const adminEmail = 'admin@codegian.com'
    const adminPassword = 'admin123'

    const isAdminLogin = user.email.trim().toLowerCase() === adminEmail && user.password === adminPassword

    setUser((previousUser) => ({
      ...previousUser,
      name: previousUser.name.trim() || (isAdminLogin ? 'Admin' : 'Student'),
      role: isAdminLogin ? 'Admin' : 'Student',
    }))
    setIsLoggedIn(true)
    setShowIntro(true)
  }

  const requestMicrophonePermission = async () => {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setMicSupported(false)
      setMicPermission('denied')
      setVoiceError('Microphone not supported in this browser.')
      return
    }

    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
      setMicSupported(true)
      setMicPermission('granted')
      setVoiceError('Microphone permission granted.')
    } catch (err) {
      setMicSupported(true)
      setMicPermission('denied')
      setVoiceError('Microphone permission denied. You can type answers instead.')
    }
  }

  const handleAnswerChange = (value) => {
    setAnswers((previousAnswers) => ({
      ...previousAnswers,
      [currentQuestion.id]: value,
    }))
  }

  const handleNextQuestion = () => {
    if (currentIndex < filteredQuestions.length - 1) {
      setCurrentIndex((previousIndex) => previousIndex + 1)
    }
  }

  const handlePreviousQuestion = () => {
    if (currentIndex > 0) {
      setCurrentIndex((previousIndex) => previousIndex - 1)
    }
  }

  const speakQuestion = () => {
    if (!currentQuestion || typeof window === 'undefined' || !('speechSynthesis' in window)) {
      return
    }

    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(currentQuestion.text)
    utterance.rate = 1
    utterance.pitch = 1
    utterance.lang = 'en-US'
    window.speechSynthesis.speak(utterance)
  }

  const startVoiceCaptureForCurrentQuestion = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      setVoiceError('Voice recognition is not supported in this browser. Please use Chrome or Edge.')
      return
    }

    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop()
      setIsListening(false)
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => {
      setVoiceError('')
      setIsListening(true)
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      const existingText = answers[currentQuestion.id] ?? ''
      const nextValue = existingText ? `${existingText}\n${transcript}` : transcript
      handleAnswerChange(nextValue)
    }

    recognition.onerror = (event) => {
      const message = event.error === 'not-allowed'
        ? 'Microphone permission is blocked. Please allow microphone access and try again.'
        : 'Unable to capture speech. Please try again.'
      setVoiceError(message)
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current = recognition
    try {
      recognition.start()
    } catch {
      setVoiceError('Microphone is busy. Please try again in a moment.')
    }
  }

  const toggleVoiceInput = () => {
    startVoiceCaptureForCurrentQuestion()
  }

  const runCode = () => {
    if (!currentQuestion || currentQuestion.type !== 'coding') return

    try {
      const logs = []
      const customConsole = {
        log: (...values) => {
          logs.push(values.map((value) => String(value)).join(' '))
        },
        error: (...values) => {
          logs.push(`Error: ${values.map((value) => String(value)).join(' ')}`)
        },
      }

      const runner = new Function('console', `${answers[currentQuestion.id] ?? currentQuestion.starterCode}`)
      runner(customConsole)
      setCodeOutput(logs.length > 0 ? logs.join('\n') : 'Code executed successfully with no output.')
    } catch (error) {
      setCodeOutput(error.message)
    }
  }

  const finishInterview = async (autoSubmitted = false) => {
    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    const results = []
    let totalScore = 0

    for (const question of filteredQuestions) {
      const answer = (answers[question.id] ?? '').trim()
      const entry = {
        id: question.id,
        question: question.text,
        category: question.category,
        answer,
        isCorrect: false,
        details: {},
      }

      try {
        if (!answer) {
          entry.details = { note: 'No answer provided' }
          entry.isCorrect = false
        } else if (question.type === 'theoretical') {
          const payload = {
            question_id: question.id,
            question_text: question.text,
            accepted_keywords: question.acceptedKeywords ?? [],
            reference_answers: question.referenceAnswers ?? null,
            student_answer: answer,
          }

          const resp = await fetch(`${API_BASE}/evaluate/theory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          })
          if (resp.ok) {
            const data = await resp.json()
            entry.details = data
            entry.isCorrect = data.is_correct
            totalScore += data.score || 0
          } else {
            entry.details = { error: 'Evaluation service error' }
          }
        } else if (question.type === 'coding') {
          const payload = { language: question.compiler ?? language, code: answer }
          const resp = await fetch(`${API_BASE}/run/code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          })
          if (resp.ok) {
            const data = await resp.json()
            entry.details = data
            // Determine correctness: pass or expectedOutput match
            const passed = data.passed || (question.expectedOutput && (data.stdout || '').includes(String(question.expectedOutput)))
            entry.isCorrect = !!passed
            totalScore += entry.isCorrect ? 100 : 0
          } else {
            entry.details = { error: 'Code runner error' }
          }
        }
      } catch (e) {
        entry.details = { error: String(e) }
      }

      results.push(entry)
    }

    const answeredCount = results.filter((r) => r.answer && r.answer.length > 0).length
    const overallScore = Math.round(totalScore / Math.max(1, filteredQuestions.length))

    // Derive strengths/weak areas from per-question results
    const correctCount = results.filter((r) => r.isCorrect).length
    const strengths = []
    const weakAreas = []
    if (correctCount / filteredQuestions.length >= 0.7) strengths.push('Strong technical accuracy')
    else weakAreas.push('Many answers missed key points')
    // analyze categories
    const byCategory = {}
    results.forEach((r) => {
      byCategory[r.category] = byCategory[r.category] || { correct: 0, total: 0 }
      byCategory[r.category].total += 1
      if (r.isCorrect) byCategory[r.category].correct += 1
    })
    Object.entries(byCategory).forEach(([cat, stats]) => {
      if (stats.correct / stats.total >= 0.7) strengths.push(`Strong in ${cat}`)
      else weakAreas.push(`Weaker in ${cat}`)
    })

    setReport({
      overallScore,
      submittedMode: autoSubmitted ? 'Auto-timed submission' : 'Manual submission',
      answeredCount,
      totalQuestions: filteredQuestions.length,
      strengths,
      weakAreas,
      answers: results,
    })

    setInterviewStarted(false)
  }

  const handleAddQuestion = (event) => {
    event.preventDefault()
    if (!newQuestion.text.trim()) return

    const type = questionTypeOptions[Math.floor(Math.random() * questionTypeOptions.length)]

    setQuestions((previousQuestions) => [
      {
        id: Date.now(),
        category: newQuestion.category,
        type,
        level: previousQuestions.length + 1,
        text: newQuestion.text.trim(),
        compiler: 'JavaScript',
      },
      ...previousQuestions,
    ])
    setNewQuestion({ category: 'Frontend', text: '', type: 'theoretical' })
  }
  return (
    <div className="app-root">
      <header className="app-header">
        <div className="brand">
          <div className="logo">DH</div>
          <div>
            <h1>Data Hunters</h1>
            <p className="sub">AI Mock Interview</p>
          </div>
        </div>
        <div className="header-actions">
          <div className="timer-pill">{timer}s</div>
          {isLoggedIn && <button className="secondary-button" onClick={() => setViewingAllQuestions(!viewingAllQuestions)}>Questions</button>}
          <button className="ghost-button" onClick={() => setShowIntro(true)}>Intro</button>
          <button className="primary-button" onClick={() => setIsLoggedIn(false)}>{isLoggedIn ? 'Logout' : 'Login'}</button>
        </div>
      </header>

      <div className="layout">
        <nav className="left-nav">
          <div className="user-compact">
            <div className="avatar">{user.name.slice(0,1).toUpperCase()}</div>
            <div>
              <div className="name">{user.name}</div>
              <div className="role">{user.role}</div>
            </div>
          </div>

          <div className="progress">
            <div className="progress-title">Progress</div>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${((currentIndex)/Math.max(1,filteredQuestions.length-1))*100}%`}} />
            </div>
            <div className="progress-meta">Q {currentIndex+1} / {filteredQuestions.length}</div>
          </div>

          <div className="nav-actions">
            <button className="secondary-button" onClick={() => { setShowIntro(true); }}>Re-open Intro</button>
            <button className="secondary-button" onClick={() => { setCurrentIndex(0); }}>Restart Round</button>
          </div>
        </nav>

        <main className="main-area">
          {!isLoggedIn ? (
            <section className="welcome-card">
              <h2>Welcome to your AI practice interview</h2>
              <p>Sign in to begin — students provide credentials, admins can manage the question bank.</p>
              <form onSubmit={handleLogin} className="compact-login">
                <input value={user.name} onChange={(e)=>setUser({...user,name:e.target.value})} placeholder="Your name" />
                <input value={user.email} onChange={(e)=>setUser({...user,email:e.target.value})} placeholder="you@example.com" />
                <input type="password" value={user.password} onChange={(e)=>setUser({...user,password:e.target.value})} placeholder="password" />
                <div className="login-actions">
                  <button className="primary-button" type="submit">Continue</button>
                </div>
                <small>Admin: admin@codegian.com / admin123</small>
              </form>
            </section>
          ) : viewingAllQuestions ? (
            <section className="questions-list-section">
              <h2>All Questions Bank</h2>
              <div className="category-filters">
                {categories.map(cat => (
                  <button 
                    key={cat}
                    className={`filter-btn ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
              <div className="questions-grid">
                {defaultQuestions
                  .filter(q => selectedCategory === 'All' || q.category === selectedCategory)
                  .map((q) => (
                    <div key={q.id} className="question-item">
                      <div className="question-header">
                        <div className="question-id">Q{q.id}</div>
                        <div className="question-meta">
                          <span className="badge category">{q.category}</span>
                          <span className="badge type">{q.type}</span>
                          <span className="badge level">L{q.level}</span>
                        </div>
                      </div>
                      <div className="question-body">
                        <p className="question-text-preview">{q.text}</p>
                      </div>
                      <div className="question-footer">
                        {q.compiler && <span className="compiler-tag">📝 {q.compiler}</span>}
                        {q.starterCode && <span className="starter-tag">⭐ Has starter code</span>}
                      </div>
                    </div>
                  ))}
              </div>
              <button className="secondary-button" onClick={() => setViewingAllQuestions(false)} style={{marginTop: '20px'}}>Back to Interview</button>
            </section>
          ) : (
            <section className="question-stage">
              {showIntro && (
                <div className="intro-modal">
                  <h3>Hello {user.name}</h3>
                  <p>I will ask a series of questions. Please allow microphone access for voice answers.</p>
                  <div className="intro-controls">
                    <button className="secondary-button" onClick={requestMicrophonePermission}>Allow Microphone</button>
                    <button className="primary-button" onClick={() => { setShowIntro(false); startInterviewSession(); }}>Start Interview</button>
                  </div>
                </div>
              )}

              {!report ? (
                <div className="question-card">
                  <div className="meta-row">
                    <div className="chips">
                      <span className="chip">Level {currentDifficultyLevel}</span>
                      <span className="chip muted">{currentQuestion?.category}</span>
                    </div>
                    <div className="meta-actions">
                      <button className="speaker" onClick={speakQuestion}>🔊</button>
                      <button className="mic" onClick={toggleVoiceInput}>{isListening ? 'Stop' : 'Voice'}</button>
                    </div>
                  </div>

                  <h2 className="question-text">{currentQuestion?.text}</h2>

                  {currentQuestion?.type === 'theoretical' ? (
                    <div className="answer-area">
                      <textarea value={answers[currentQuestion?.id] ?? ''} onChange={(e)=>handleAnswerChange(e.target.value)} rows={8} placeholder="Type your answer or speak..." />
                    </div>
                  ) : (
                    <div className="code-area">
                      <div className="toolbar">
                        <select value={language} onChange={(e)=>setLanguage(e.target.value)}>
                          <option>JavaScript</option>
                          <option>Python</option>
                        </select>
                        <button className="primary-button" onClick={runCode}>Run</button>
                      </div>
                      <textarea className="code-editor" value={answers[currentQuestion.id] ?? currentQuestion.starterCode} onChange={(e)=>handleAnswerChange(e.target.value)} rows={12} />
                      <pre className="code-output">{codeOutput || 'No output yet.'}</pre>
                    </div>
                  )}

                  <div className="controls-row">
                    <button className="ghost-button" onClick={handlePreviousQuestion} disabled={currentIndex===0}>Previous</button>
                    <button className="secondary-button" onClick={handleNextQuestion}>Next</button>
                    <button className="primary-button" onClick={()=>finishInterview(false)}>Submit</button>
                  </div>
                </div>
              ) : (
                <div className="report-panel">
                  <h2>Performance Report — {report.overallScore}/100</h2>
                  <div className="report-grid">
                    <div>
                      <h4>Strengths</h4>
                      <ul>{report.strengths.map(s=> <li key={s}>{s}</li>)}</ul>
                    </div>
                    <div>
                      <h4>Weak Areas</h4>
                      <ul>{report.weakAreas.map(s=> <li key={s}>{s}</li>)}</ul>
                    </div>
                  </div>

                  <div className="answer-list">
                    {report.answers.map((a, i)=> (
                      <div key={a.id || i} className={`answer-row ${a.isCorrect ? 'ok' : 'bad'}`}>
                        <div className="q">Q{i+1}. {a.question}</div>
                        <div className="a">{a.answer || 'No answer'}</div>
                        <div className="detail">{a.details?.feedback ?? a.details?.stdout ?? ''}</div>
                      </div>
                    ))}
                  </div>

                  <div className="report-actions">
                    <button className="secondary-button" onClick={()=>startInterviewSession()}>Retake</button>
                  </div>
                </div>
              )}
            </section>
          )}
        </main>

        <aside className="right-panel">
          <div className="panel mini">
            <h4>Session Info</h4>
            <p>Questions: <strong>{filteredQuestions.length}</strong></p>
            <p>Answered: <strong>{Object.values(answers).filter(v=>v&&v.trim()).length}</strong></p>
            <p>Mic: <strong>{micPermission}</strong></p>
          </div>

          {isAdmin && (
            <div className="panel mini">
              <h4>Admin</h4>
              <button className="secondary-button" onClick={()=>setQuestions(defaultQuestions)}>Reset Bank</button>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}

export default App
