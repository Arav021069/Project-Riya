import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Plus, Send, Trash2, X } from 'lucide-react';
import './App.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Session {
  id: string;
  title: string;
  timestamp: string;
}

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeModel, setActiveModel] = useState('gemma4:31b-cloud');
  const [showModal, setShowModal] = useState(false);
  
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchActiveModel = async () => {
      try {
        const res = await fetch('/api/models');
        const data = await res.json();
        if (data.models && data.models.length > 0) {
          setActiveModel(data.models[0]);
        }
      } catch (err) {
        console.error('Failed to fetch models:', err);
      }
    };
    void fetchActiveModel();
  }, []);

  const getModelDetails = (modelName: string) => {
    const nameLower = modelName.toLowerCase();
    if (nameLower.includes('31b')) {
      return {
        family: 'Gemma 2 / Gemma 4',
        parameters: '31 Billion',
        quantization: 'Q4_K_M (Recommended)',
        format: 'GGUF',
        type: 'Local LLM (Cloud Optimized)',
        description: 'A powerful, highly optimized state-of-the-art open model designed by Google, delivering exceptional reasoning and code understanding capabilities.'
      };
    } else if (nameLower.includes('e2b')) {
      return {
        family: 'Gemma 2 / Gemma 4',
        parameters: '9 Billion / 27 Billion',
        quantization: 'e2b sandbox preview',
        format: 'GGUF',
        type: 'Local LLM (Sandbox)',
        description: 'A customized local Gemma model integrated with execution sandbox tool capabilities, optimized for code generation and tool usage.'
      };
    }
    return {
      family: 'Gemma / Llama',
      parameters: 'Unknown',
      quantization: 'Standard',
      format: 'GGUF / Ollama',
      type: 'Local LLM',
      description: 'A locally hosted large language model running via Ollama on your system.'
    };
  };
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const fetchSessions = useCallback(async () => {
    try {
      const res = await fetch('/api/sessions');
      const data = await res.json();
      setSessions(data);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    const fetchInitialSessions = async () => {
      try {
        const res = await fetch('/api/sessions');
        const data = await res.json();
        if (!ignore) {
          setSessions(data);
        }
      } catch (err) {
        console.error('Failed to fetch sessions:', err);
      }
    };
    void fetchInitialSessions();
    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const loadSession = async (sessionId: string) => {
    if (isStreaming) return;
    setCurrentSessionId(sessionId);
    try {
      const res = await fetch(`/api/sessions/${sessionId}`);
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  const startNewChat = () => {
    if (isStreaming) return;
    setCurrentSessionId(null);
    setMessages([]);
    setInputValue('');
  };

  const deleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this conversation?')) return;
    
    try {
      const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
      if (res.ok) {
        if (currentSessionId === sessionId) {
          startNewChat();
        }
        fetchSessions();
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const message = inputValue.trim();
    if (!message || isStreaming) return;

    const userMessage: Message = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsStreaming(true);

    // Placeholder for AI response
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, session_id: currentSessionId })
      });

      if (!currentSessionId) {
        const newSid = response.headers.get('X-Session-ID');
        if (newSid) setCurrentSessionId(newSid);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          accumulatedText += decoder.decode(value, { stream: true });
          
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1].content = accumulatedText;
            return newMessages;
          });
        }
      }
      fetchSessions(); // Refresh sidebar
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].content = 'Error: Could not connect to the server.';
        return newMessages;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  return (
    <div className="root-container" style={{ display: 'flex', width: '100%', height: '100%' }}>
      <div className="sidebar">
        <button className="new-chat-btn" onClick={startNewChat}>
          <Plus size={16} /> New chat
        </button>
        <div className="history-list">
          {sessions.map(session => (
            <div 
              key={session.id} 
              className={`history-item ${session.id === currentSessionId ? 'active' : ''}`}
              onClick={() => loadSession(session.id)}
            >
              <span className="history-text">{session.title}</span>
              <button className="delete-btn" onClick={(e) => deleteSession(e, session.id)}>
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="main-content">
        <div className="header-bar">
          <div className="header-logo">
            <span className="logo-accent">RIYA</span>GPT
          </div>
          <div className="header-model-selector" onClick={() => setShowModal(true)}>
            <span className="model-indicator-dot"></span>
            <span className="model-name-text">{activeModel}</span>
          </div>
        </div>

        <div className="chat-container" ref={chatContainerRef}>
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role === 'user' ? 'user-message-wrapper' : 'ai-message-wrapper'}`}>
              <div className="message-content">
                <div className={`avatar ${msg.role === 'user' ? 'user-avatar' : 'ai-avatar'}`}>
                  {msg.role === 'user' ? 'U' : 'AI'}
                </div>
                <div className="text">
                  {msg.role === 'user' ? (
                    msg.content
                  ) : (
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      components={{
                        /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
                        code({ inline, className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
                              style={vscDarkPlus as any}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          );
                        }
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="input-container">
          <form className="input-form" onSubmit={handleSend}>
            <textarea
              ref={textareaRef}
              className="user-input"
              placeholder="Send a message..."
              rows={1}
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
            />
            <button type="submit" className="send-btn" disabled={!inputValue.trim() || isStreaming}>
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Model Specifications</h3>
              <button className="modal-close-btn" onClick={() => setShowModal(false)}>
                <X size={18} />
              </button>
            </div>
            <div className="modal-body">
              <div className="model-info-hero">
                <div className="model-title-large">{activeModel}</div>
                <div className="model-type-badge">{getModelDetails(activeModel).type}</div>
              </div>
              <p className="model-description">{getModelDetails(activeModel).description}</p>
              <div className="model-spec-grid">
                <div className="spec-card">
                  <span className="spec-label">Family</span>
                  <span className="spec-value">{getModelDetails(activeModel).family}</span>
                </div>
                <div className="spec-card">
                  <span className="spec-label">Parameters</span>
                  <span className="spec-value">{getModelDetails(activeModel).parameters}</span>
                </div>
                <div className="spec-card">
                  <span className="spec-label">Quantization</span>
                  <span className="spec-value">{getModelDetails(activeModel).quantization}</span>
                </div>
                <div className="spec-card">
                  <span className="spec-label">Format</span>
                  <span className="spec-value">{getModelDetails(activeModel).format}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
