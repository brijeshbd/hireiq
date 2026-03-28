import { useState } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function JDAnalyzer() {
  const [jd, setJd]           = useState('');
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!jd.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API}/api/analyze-jd`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_description: jd })
      });
      const data = await response.json();
      setResult(data.analysis);
    } catch (error) {
      alert('Error connecting to server!');
    }

    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

      <div className="component-header">
        <h2>🔍 Job Description Analyzer</h2>
        <p>Paste any job description to extract key skills, requirements, and insights</p>
      </div>

      <div className="component-body">
        <textarea
          value={jd}
          onChange={e => setJd(e.target.value)}
          placeholder="Paste the job description here..."
          rows={8}
        />

        <button
          className="btn btn-primary"
          onClick={analyze}
          disabled={loading || !jd.trim()}
          style={{ marginTop: '16px' }}
        >
          {loading ? 'Analyzing...' : '🔍 Analyze JD'}
        </button>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            Analyzing job description...
          </div>
        )}

        {result && (
          <div className="result-box">

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
              <div>
                <p style={{ color: '#64748b', fontSize: '12px' }}>ROLE</p>
                <p style={{ fontWeight: '700', fontSize: '16px' }}>{result.role || 'N/A'}</p>
              </div>
              <div>
                <p style={{ color: '#64748b', fontSize: '12px' }}>COMPANY TYPE</p>
                <p style={{ fontWeight: '700', fontSize: '16px' }}>{result.company_type || 'N/A'}</p>
              </div>
              <div>
                <p style={{ color: '#64748b', fontSize: '12px' }}>EXPERIENCE</p>
                <p style={{ fontWeight: '700', fontSize: '16px' }}>{result.experience_years || 'N/A'}</p>
              </div>
              <div>
                <p style={{ color: '#64748b', fontSize: '12px' }}>REMOTE</p>
                <p style={{ fontWeight: '700', fontSize: '16px' }}>
                  {result.remote_friendly === true ? '✅ Yes' :
                   result.remote_friendly === false ? '❌ No' : 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ color: '#64748b', fontSize: '12px' }}>SALARY</p>
                <p style={{ fontWeight: '700', fontSize: '16px' }}>{result.salary_range || 'Not mentioned'}</p>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '8px', color: '#10b981' }}>✅ Required Skills</h4>
              {(result.required_skills || []).map((s, i) => (
                <span key={i} className="tag tag-blue">{s}</span>
              ))}
            </div>

            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '8px', color: '#f59e0b' }}>⭐ Nice to Have</h4>
              {(result.nice_to_have || []).map((s, i) => (
                <span key={i} className="tag tag-purple">{s}</span>
              ))}
            </div>

            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '8px', color: '#3b82f6' }}>🎭 Culture Signals</h4>
              {(result.culture_signals || []).map((s, i) => (
                <span key={i} className="tag tag-green">{s}</span>
              ))}
            </div>

            <div style={{
              background: '#0f1117',
              borderRadius: '8px',
              padding: '14px',
              marginTop: '8px'
            }}>
              <p style={{ color: '#64748b', fontSize: '12px', marginBottom: '6px' }}>SUMMARY</p>
              <p style={{ color: '#e2e8f0' }}>{result.summary}</p>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

export default JDAnalyzer;