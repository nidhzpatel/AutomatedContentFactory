import React, { useState } from 'react';

function App() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('blog');
  const [result, setResult] = useState(null);
  const [copiedFormat, setCopiedFormat] = useState(null);
  const [stripMarkdown, setStripMarkdown] = useState(true);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      const data = await response.json();
      setResult(data);
      setActiveTab('blog');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const cleanMarkdownText = (text) => {
    if (!text) return '';
    return text
      .replace(/^#{1,6}\s+/gm, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/__(.*?)__/g, '$1')
      .replace(/_(.*?)_/g, '$1')
      .replace(/`(.*?)`/g, '$1')
      .replace(/```[\s\S]*?```/g, (match) => match.replace(/```[a-z]*/gi, '').replace(/```/g, ''))
      .replace(/\[(.*?)\]\((.*?)\)/g, '$1 ($2)')
      .trim();
  };

  const copyToClipboard = (text, format) => {
    if (!text) return;
    const finalText = stripMarkdown ? cleanMarkdownText(text) : text;
    navigator.clipboard.writeText(finalText);
    setCopiedFormat(format);
    setTimeout(() => setCopiedFormat(null), 2500);
  };

  const downloadFile = (filename, content) => {
    if (!content) return;
    const finalText = stripMarkdown ? cleanMarkdownText(content) : content;
    const ext = filename.endsWith('.txt') || stripMarkdown ? 'txt' : 'md';
    const cleanFilename = filename.replace(/\.(md|txt)$/, `.${ext}`);
    const element = document.createElement('a');
    const file = new Blob([finalText], { type: 'text/plain;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = cleanFilename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const getActiveContent = () => {
    if (!result) return { text: '', filename: 'content.md', label: '' };
    switch (activeTab) {
      case 'blog':
        return {
          text: result.blog_post?.content || '',
          filename: `${topic.toLowerCase().replace(/[^a-z0-9]/g, '_')}_blog.md`,
          label: 'Blog Article',
        };
      case 'linkedin':
        return {
          text: result.linkedin_post?.content || '',
          filename: `${topic.toLowerCase().replace(/[^a-z0-9]/g, '_')}_linkedin.txt`,
          label: 'LinkedIn Post',
        };
      case 'x':
        return {
          text: result.x_post?.content || '',
          filename: `${topic.toLowerCase().replace(/[^a-z0-9]/g, '_')}_x_post.txt`,
          label: 'X / Twitter Post & Thread',
        };
      case 'overview':
        return {
          text: result.detailed_overview?.content || '',
          filename: `${topic.toLowerCase().replace(/[^a-z0-9]/g, '_')}_detailed_overview.md`,
          label: 'Detailed Technical Overview & References',
        };
      default:
        return { text: '', filename: 'content.md', label: '' };
    }
  };

  const currentContent = getActiveContent();
  const displayText = stripMarkdown ? cleanMarkdownText(currentContent.text) : currentContent.text;

  return (
    <div style={styles.pageContainer}>
      <header style={styles.header}>
        <div style={styles.badge}>⚡ CrewAI Multi-Agent Architecture (5 Specialized Agents)</div>
        <h1 style={styles.title}>Automated Content Factory</h1>
        <p style={styles.subtitle}>
          Autonomous Multi-Agent Content Pipeline with Self-Correcting Revision Loops & Security Guardrails.
        </p>
      </header>

      <main style={styles.main}>
        <form onSubmit={handleGenerate} style={styles.form}>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a topic (e.g. Prompt Injection, AI Security)..."
            style={styles.input}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !topic.trim()} style={styles.button}>
            {loading ? '⚡ Running 5-Agent Crew...' : '🚀 Execute Crew Flow'}
          </button>
        </form>

        {loading && (
          <div style={styles.loadingContainer}>
            <div style={styles.pulseDot}></div>
            <p style={styles.loadingText}>
              Orchestrating Researcher ➔ Writer ➔ Critic ➔ Editor ➔ Fact-Checker Agents...
            </p>
          </div>
        )}

        {result && result.status === 'failed_security_guardrail' && (
          <div style={styles.errorAlert}>
            🚨 <strong>Security Guardrail Triggered:</strong> {result.error_message}
          </div>
        )}

        {result && result.status === 'completed' && (
          <div style={styles.resultCard}>
            {/* Execution Metrics Bar */}
            <div style={styles.metricsBar}>
              <div style={styles.metricItem}>
                <span style={styles.metricLabel}>⏱️ Latency</span>
                <span style={styles.metricValue}>{(result.metrics?.latency_ms / 1000).toFixed(2)}s</span>
              </div>
              <div style={styles.metricItem}>
                <span style={styles.metricLabel}>🔄 Revision Loops</span>
                <span style={styles.metricValue}>{result.metrics?.revision_count || 0} / 3</span>
              </div>
              <div style={styles.metricItem}>
                <span style={styles.metricLabel}>🛡️ Fact-Check Score</span>
                <span style={styles.metricValue}>{(result.metrics?.fact_check_score * 100).toFixed(0)}%</span>
              </div>
              <div style={styles.metricItem}>
                <span style={styles.metricLabel}>🎯 Hallucination Rate</span>
                <span style={styles.metricValue}>{(result.metrics?.hallucination_rate * 100).toFixed(0)}%</span>
              </div>
              <div style={styles.metricItem}>
                <span style={styles.metricLabel}>📝 Word Count</span>
                <span style={styles.metricValue}>{result.metrics?.word_count || 0}</span>
              </div>
            </div>

            <div style={styles.tabHeader}>
              <button
                style={{ ...styles.tabButton, ...(activeTab === 'blog' ? styles.activeTab : {}) }}
                onClick={() => setActiveTab('blog')}
              >
                📝 Blog Post
              </button>
              <button
                style={{ ...styles.tabButton, ...(activeTab === 'linkedin' ? styles.activeTab : {}) }}
                onClick={() => setActiveTab('linkedin')}
              >
                💼 LinkedIn
              </button>
              <button
                style={{ ...styles.tabButton, ...(activeTab === 'x' ? styles.activeTab : {}) }}
                onClick={() => setActiveTab('x')}
              >
                🐦 X (Twitter)
              </button>
              <button
                style={{ ...styles.tabButton, ...(activeTab === 'overview' ? styles.activeTab : {}) }}
                onClick={() => setActiveTab('overview')}
              >
                📚 Detailed Overview
              </button>
            </div>

            <div style={styles.contentBody}>
              <div style={styles.contentActions}>
                <span style={styles.contentTypeTitle}>{currentContent.label}</span>
                <div style={styles.actionControls}>
                  <label style={styles.toggleLabel}>
                    <input
                      type="checkbox"
                      checked={stripMarkdown}
                      onChange={(e) => setStripMarkdown(e.target.checked)}
                      style={styles.checkbox}
                    />
                    Clean Plain Text (remove # & **)
                  </label>

                  <div style={styles.iconButtonGroup}>
                    <button
                      title="Copy to Clipboard"
                      aria-label="Copy to Clipboard"
                      style={copiedFormat === activeTab ? styles.copiedIconBtn : styles.iconBtn}
                      onClick={() => copyToClipboard(currentContent.text, activeTab)}
                    >
                      {copiedFormat === activeTab ? '✓' : '📋'}
                    </button>

                    <button
                      title="Download File"
                      aria-label="Download File"
                      style={styles.iconBtn}
                      onClick={() => downloadFile(currentContent.filename, currentContent.text)}
                    >
                      📥
                    </button>
                  </div>
                </div>
              </div>

              <textarea
                readOnly
                value={displayText}
                style={styles.textarea}
                rows={16}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

const styles = {
  pageContainer: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)',
    color: '#f8fafc',
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    padding: '3rem 1.5rem',
  },
  header: {
    textAlign: 'center',
    maxWidth: '850px',
    margin: '0 auto 3rem auto',
  },
  badge: {
    display: 'inline-block',
    padding: '0.4rem 1rem',
    borderRadius: '9999px',
    background: 'rgba(99, 102, 241, 0.15)',
    border: '1px solid rgba(129, 140, 248, 0.3)',
    color: '#a5b4fc',
    fontSize: '0.875rem',
    fontWeight: '600',
    marginBottom: '1rem',
  },
  title: {
    fontSize: '2.75rem',
    fontWeight: '800',
    background: 'linear-gradient(90deg, #6366f1, #a855f7, #ec4899)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    margin: '0 0 1rem 0',
    letterSpacing: '-0.02em',
  },
  subtitle: {
    fontSize: '1.125rem',
    color: '#94a3b8',
    lineHeight: '1.6',
    margin: 0,
  },
  main: {
    maxWidth: '950px',
    margin: '0 auto',
  },
  form: {
    display: 'flex',
    gap: '12px',
    marginBottom: '2rem',
    background: 'rgba(30, 41, 59, 0.7)',
    padding: '8px',
    borderRadius: '16px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(12px)',
  },
  input: {
    flex: 1,
    padding: '1rem 1.25rem',
    fontSize: '1rem',
    background: 'transparent',
    border: 'none',
    color: '#fff',
    outline: 'none',
  },
  button: {
    padding: '1rem 1.75rem',
    fontSize: '1rem',
    fontWeight: '600',
    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    color: '#ffffff',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.2s ease-in-out',
    boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)',
  },
  loadingContainer: {
    textAlign: 'center',
    padding: '2.5rem',
    background: 'rgba(30, 41, 59, 0.4)',
    borderRadius: '16px',
    border: '1px solid rgba(255, 255, 255, 0.05)',
  },
  loadingText: {
    color: '#cbd5e1',
    fontSize: '1rem',
  },
  errorAlert: {
    padding: '1.25rem',
    borderRadius: '12px',
    background: 'rgba(239, 68, 68, 0.15)',
    border: '1px solid rgba(239, 68, 68, 0.4)',
    color: '#fca5a5',
    marginBottom: '2rem',
  },
  resultCard: {
    background: 'rgba(30, 41, 59, 0.8)',
    borderRadius: '20px',
    border: '1px solid rgba(255, 255, 255, 0.12)',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
    overflow: 'hidden',
  },
  metricsBar: {
    display: 'flex',
    justifyContent: 'space-around',
    padding: '1rem 1.5rem',
    background: 'rgba(15, 23, 42, 0.7)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    flexWrap: 'wrap',
    gap: '12px',
  },
  metricItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: '0.75rem',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    marginBottom: '4px',
  },
  metricValue: {
    fontSize: '1.1rem',
    fontWeight: '700',
    color: '#a5b4fc',
  },
  tabHeader: {
    display: 'flex',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
    background: 'rgba(15, 23, 42, 0.5)',
  },
  tabButton: {
    flex: 1,
    padding: '1.1rem',
    background: 'transparent',
    border: 'none',
    color: '#94a3b8',
    fontSize: '0.95rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  activeTab: {
    color: '#818cf8',
    borderBottom: '3px solid #6366f1',
    background: 'rgba(99, 102, 241, 0.1)',
  },
  contentBody: {
    padding: '1.75rem',
  },
  contentActions: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
    flexWrap: 'wrap',
    gap: '10px',
  },
  contentTypeTitle: {
    fontWeight: '700',
    fontSize: '1.1rem',
    color: '#f1f5f9',
  },
  actionControls: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  toggleLabel: {
    fontSize: '0.85rem',
    color: '#cbd5e1',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
    userSelect: 'none',
  },
  checkbox: {
    accentColor: '#6366f1',
    cursor: 'pointer',
  },
  iconButtonGroup: {
    display: 'flex',
    gap: '8px',
  },
  iconBtn: {
    width: '42px',
    height: '42px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#334155',
    color: '#f8fafc',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    borderRadius: '10px',
    fontSize: '1.2rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  copiedIconBtn: {
    width: '42px',
    height: '42px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#10b981',
    color: '#ffffff',
    border: 'none',
    borderRadius: '10px',
    fontSize: '1.2rem',
    fontWeight: 'bold',
    cursor: 'default',
  },
  textarea: {
    width: '100%',
    padding: '1.25rem',
    fontSize: '0.95rem',
    lineHeight: '1.6',
    background: '#0f172a',
    color: '#e2e8f0',
    border: '1px solid #334155',
    borderRadius: '12px',
    resize: 'vertical',
    fontFamily: 'monospace',
    outline: 'none',
    boxSizing: 'border-box',
  },
};

export default App;
