import { useState } from 'react';

const API = 'http://localhost:8000';

function ResumeAnalyzer() {
  const [resume, setResume]   = useState('');
  const [jd, setJd]           = useState('');
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!resume.trim() || !jd.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API}/api/analyze-resume`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume:          resume,
          job_description: jd
        })
      });
      const data = await response.json();
      setResult(data.analysis);
    } catch (error) {
      alert('Error connecting to server!');
    }

    setLoading(false);
  };

  const getScoreClass = (score) => {
    if (score >= 75) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

      <div className="component-header">
        <h2>📄 Resume Analyzer</h2>
        <p>Paste your resume and a job description to get a match score and improvement tips</p>
      </div>

      <div className="component-body">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px', display: 'block' }}>
              Your Resume
            </label>
            <textarea
              value={resume}
              onChange={e => setResume(e.target.value)}
              placeholder="Paste your resume text here..."
              rows={12}
            />
          </div>
          <div>
            <label style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px', display: 'block' }}>
              Job Description
            </label>
            <textarea
              value={jd}
              onChange={e => setJd(e.target.value)}
              placeholder="Paste the job description here..."
              rows={12}
            />
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={analyze}
          disabled={loading || !resume.trim() || !jd.trim()}
          style={{ marginTop: '16px' }}
        >
          {loading ? 'Analyzing...' : '🔍 Analyze Match'}
        </button>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            Analyzing your resume...
          </div>
        )}

        {result && (
          <div className="result-box">

            {/* Score */}
            <div className={`score-badge ${getScoreClass(result.match_score)}`}>
              {result.match_score >= 75 ? '🌟' : result.match_score >= 50 ? '✅' : '⚠️'}
              Match Score: {result.match_score}%
            </div>

            {/* Summary */}
            <p style={{ marginBottom: '20px', color: '#94a3b8' }}>
              {result.summary}
            </p>

            {/* Matching Skills */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '8px', color: '#10b981' }}>
                ✅ Matching Skills
              </h4>
              {(result.matching_skills || []).map((skill, i) => (
                <span key={i} className="tag tag-green">{skill}</span>
              ))}
            </div>

            {/* Missing Skills */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '8px', color: '#ef4444' }}>
                ❌ Missing Skills
              </h4>
              {(result.missing_skills || []).map((skill, i) => (
                <span key={i} className="tag tag-red">{skill}</span>
              ))}
            </div>

            {/* Improvements */}
            <div>
              <h4 style={{ marginBottom: '8px', color: '#3b82f6' }}>
                💡 Improvements
              </h4>
              {(result.improvements || []).map((tip, i) => (
                <p key={i} style={{ marginBottom: '6px', color: '#94a3b8' }}>
                  • {tip}
                </p>
              ))}
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

export default ResumeAnalyzer;