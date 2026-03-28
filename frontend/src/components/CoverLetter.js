import { useState } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function CoverLetter() {
  const [resume,      setResume]      = useState('');
  const [jd,          setJd]          = useState('');
  const [company,     setCompany]     = useState('');
  const [tone,        setTone]        = useState('professional');
  const [result,      setResult]      = useState('');
  const [loading,     setLoading]     = useState(false);

  const generate = async () => {
    if (!resume.trim() || !jd.trim() || !company.trim()) return;
    setLoading(true);
    setResult('');

    try {
      const response = await fetch(`${API}/api/cover-letter`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume:          resume,
          job_description: jd,
          company_name:    company,
          tone:            tone
        })
      });
      const data = await response.json();
      setResult(data.cover_letter);
    } catch (error) {
      alert('Error connecting to server!');
    }

    setLoading(false);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result);
    alert('Copied to clipboard!');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

      <div className="component-header">
        <h2>✍️ Cover Letter Generator</h2>
        <p>Generate a tailored cover letter for any job application</p>
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
              placeholder="Paste your resume..."
              rows={8}
            />
          </div>
          <div>
            <label style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px', display: 'block' }}>
              Job Description
            </label>
            <textarea
              value={jd}
              onChange={e => setJd(e.target.value)}
              placeholder="Paste the job description..."
              rows={8}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
          <div>
            <label style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px', display: 'block' }}>
              Company Name
            </label>
            <input
              value={company}
              onChange={e => setCompany(e.target.value)}
              placeholder="e.g. Mercari, Atlassian, Razorpay"
            />
          </div>
          <div>
            <label style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px', display: 'block' }}>
              Tone
            </label>
            <select
              value={tone}
              onChange={e => setTone(e.target.value)}
              style={{
                width: '100%', padding: '12px 16px',
                background: '#1a1f2e', border: '1px solid #2d3748',
                borderRadius: '10px', color: '#e2e8f0', fontSize: '14px'
              }}
            >
              <option value="professional">Professional</option>
              <option value="confident">Confident & Direct</option>
              <option value="friendly">Friendly</option>
            </select>
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={generate}
          disabled={loading || !resume.trim() || !jd.trim() || !company.trim()}
          style={{ marginTop: '16px' }}
        >
          {loading ? 'Generating...' : '✍️ Generate Cover Letter'}
        </button>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            Writing your cover letter...
          </div>
        )}

        {result && (
          <div className="result-box" style={{ position: 'relative' }}>
            <button
              onClick={copyToClipboard}
              className="btn btn-primary"
              style={{ position: 'absolute', top: '16px', right: '16px', padding: '6px 14px', fontSize: '12px' }}
            >
              📋 Copy
            </button>
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', paddingTop: '8px' }}>
              {result}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default CoverLetter;