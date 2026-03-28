import { useState } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const SESSION_ID = 'interview-' + Math.random().toString(36).substr(2, 9);

function Interview() {
  const [stage,      setStage]      = useState('setup');   // setup, interview, complete
  const [role,       setRole]       = useState('Java Backend Engineer');
  const [difficulty, setDifficulty] = useState('medium');
  const [question,   setQuestion]   = useState('');
  const [qNumber,    setQNumber]    = useState(1);
  const [answer,     setAnswer]     = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [finalReport,setFinalReport]= useState(null);
  const [loading,    setLoading]    = useState(false);

  const startInterview = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/interview/start`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role, difficulty,
          session_id: SESSION_ID
        })
      });
      const data = await response.json();
      setQuestion(data.question);
      setStage('interview');
    } catch (error) {
      alert('Error starting interview!');
    }
    setLoading(false);
  };

  const submitAnswer = async () => {
    if (!answer.trim()) return;
    setLoading(true);

    try {
      const response = await fetch(`${API}/api/interview/answer`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: SESSION_ID,
          answer
        })
      });
      const data = await response.json();
      setEvaluation(data.evaluation);

      if (data.status === 'completed') {
        setFinalReport(data.final_report);
        setStage('complete');
      } else {
        setQuestion(data.next_question);
        setQNumber(data.question_number);
        setAnswer('');
      }
    } catch (error) {
      alert('Error submitting answer!');
    }
    setLoading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

      <div className="component-header">
        <h2>🎤 Mock Interview</h2>
        <p>Practice with AI — get scored and feedback on every answer</p>
      </div>

      <div className="component-body">

        {/* SETUP STAGE */}
        {stage === 'setup' && (
          <div style={{ maxWidth: '500px' }}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px', display: 'block' }}>
                Role
              </label>
              <select
                value={role}
                onChange={e => setRole(e.target.value)}
                style={{
                  width: '100%', padding: '12px 16px',
                  background: '#1a1f2e', border: '1px solid #2d3748',
                  borderRadius: '10px', color: '#e2e8f0', fontSize: '14px'
                }}
              >
                <option>Java Backend Engineer</option>
                <option>Senior Software Engineer</option>
                <option>LLM Engineer</option>
                <option>Full Stack Engineer</option>
              </select>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px', display: 'block' }}>
                Difficulty
              </label>
              <div style={{ display: 'flex', gap: '10px' }}>
                {['easy', 'medium', 'hard'].map(d => (
                  <button
                    key={d}
                    onClick={() => setDifficulty(d)}
                    className="btn"
                    style={{
                      flex: 1,
                      background: difficulty === d ? '#3b82f6' : '#1a1f2e',
                      color: difficulty === d ? 'white' : '#94a3b8',
                      border: `1px solid ${difficulty === d ? '#3b82f6' : '#2d3748'}`,
                      textTransform: 'capitalize'
                    }}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            <button
              className="btn btn-primary"
              onClick={startInterview}
              disabled={loading}
              style={{ width: '100%', padding: '14px' }}
            >
              {loading ? 'Starting...' : '🚀 Start Interview'}
            </button>
          </div>
        )}

        {/* INTERVIEW STAGE */}
        {stage === 'interview' && (
          <div>
            <div style={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginBottom: '20px'
            }}>
              <span style={{ color: '#64748b', fontSize: '13px' }}>
                Question {qNumber} of 5
              </span>
              <div style={{
                height: '6px', background: '#2d3748', borderRadius: '3px',
                width: '200px', overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%', width: `${(qNumber / 5) * 100}%`,
                  background: '#3b82f6', borderRadius: '3px',
                  transition: 'width 0.3s'
                }} />
              </div>
            </div>

            <div style={{
              background: '#1a1f2e', border: '1px solid #2d3748',
              borderRadius: '12px', padding: '20px', marginBottom: '20px'
            }}>
              <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '8px' }}>
                ❓ QUESTION
              </p>
              <p style={{ fontSize: '16px', lineHeight: '1.6' }}>{question}</p>
            </div>

            <textarea
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              rows={6}
            />

            <button
              className="btn btn-primary"
              onClick={submitAnswer}
              disabled={loading || !answer.trim()}
              style={{ marginTop: '12px' }}
            >
              {loading ? 'Evaluating...' : 'Submit Answer →'}
            </button>

            {/* Show evaluation */}
            {evaluation && (
              <div className="result-box" style={{ marginTop: '20px' }}>
                <div style={{
                  fontSize: '24px', fontWeight: '800',
                  color: getScoreColor(evaluation.score),
                  marginBottom: '12px'
                }}>
                  {evaluation.score}/100 — {evaluation.score_label}
                </div>
                <p style={{ marginBottom: '12px' }}>{evaluation.feedback}</p>
                {evaluation.missing_points?.length > 0 && (
                  <div>
                    <p style={{ color: '#64748b', fontSize: '13px', marginBottom: '6px' }}>
                      Could have mentioned:
                    </p>
                    {evaluation.missing_points.map((p, i) => (
                      <p key={i} style={{ color: '#94a3b8' }}>• {p}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* COMPLETE STAGE */}
        {stage === 'complete' && finalReport && (
          <div>
            <div style={{
              textAlign: 'center', marginBottom: '24px',
              padding: '24px', background: '#1a1f2e',
              borderRadius: '12px', border: '1px solid #2d3748'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '8px' }}>🎉</div>
              <h3 style={{ fontSize: '20px', marginBottom: '4px' }}>Interview Complete!</h3>
              <div style={{
                fontSize: '32px', fontWeight: '800',
                color: getScoreColor(finalReport.avg_score)
              }}>
                {finalReport.avg_score}/100
              </div>
              <p style={{ color: '#64748b', marginTop: '4px' }}>Average Score</p>
            </div>

            <div className="result-box">
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                {finalReport.report}
              </pre>
            </div>

            <button
              className="btn btn-primary"
              onClick={() => {
                setStage('setup');
                setEvaluation(null);
                setFinalReport(null);
                setQNumber(1);
                setAnswer('');
              }}
              style={{ marginTop: '16px' }}
            >
              🔄 Start New Interview
            </button>
          </div>
        )}

      </div>
    </div>
  );
}

export default Interview;