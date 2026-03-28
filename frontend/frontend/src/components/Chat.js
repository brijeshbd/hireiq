import { useState, useRef, useEffect } from 'react';

const API = 'http://localhost:8000';
const SESSION_ID = 'user-' + Math.random().toString(36).substr(2, 9);

function Chat() {
  const [messages, setMessages]   = useState([
    { role: 'assistant', content: 'Hi! I\'m HireIQ 🤖 I\'m here to help with your job search. Ask me anything!' }
  ]);
  const [input, setInput]         = useState('');
  const [loading, setLoading]     = useState(false);
  const messagesEndRef            = useRef(null);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message:    userMessage,
          session_id: SESSION_ID
        })
      });

      const data = await response.json();

      // Add AI response
      setMessages(prev => [...prev, {
        role:    'assistant',
        content: data.response
      }]);

    } catch (error) {
      setMessages(prev => [...prev, {
        role:    'assistant',
        content: '❌ Error connecting to HireIQ. Make sure the server is running!'
      }]);
    }

    setLoading(false);
  };

  // Send on Enter key
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

      {/* Header */}
      <div className="component-header">
        <h2>💬 Chat with HireIQ</h2>
        <p>Ask anything about jobs, resumes, interviews, or career advice</p>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display:       'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom:  '16px'
          }}>
            <div style={{
              maxWidth:     '75%',
              padding:      '12px 16px',
              borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
              background:   msg.role === 'user' ? '#3b82f6' : '#1a1f2e',
              border:       msg.role === 'user' ? 'none' : '1px solid #2d3748',
              fontSize:     '14px',
              lineHeight:   '1.6',
              whiteSpace:   'pre-wrap'
            }}>
              {msg.content}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#64748b' }}>
            <div className="spinner"></div>
            HireIQ is thinking...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{
        padding:      '16px 32px',
        borderTop:    '1px solid #2d3748',
        background:   '#1a1f2e',
        display:      'flex',
        gap:          '12px',
        alignItems:   'flex-end'
      }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask HireIQ anything... (Enter to send, Shift+Enter for new line)"
          rows={2}
          style={{ resize: 'none' }}
        />
        <button
          className="btn btn-primary"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{ flexShrink: 0, height: '44px' }}
        >
          Send →
        </button>
      </div>
    </div>
  );
}

export default Chat;