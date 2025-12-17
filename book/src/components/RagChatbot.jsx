/**
 * RAG Chatbot Widget for Physical AI & Humanoid Robotics Book
 *
 * A floating chat bubble that provides AI-powered Q&A using the RAG backend.
 * Supports both normal questions and selected-text context questions.
 *
 * Usage: Import and add <RagChatbot /> to your Layout component
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';

// Configuration - Change this for production deployment
const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? 'http://127.0.0.1:8001'
  : 'https://your-production-api.com';

/**
 * Main RAG Chatbot Component
 */
export default function RagChatbot() {
  // State management
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [showSelectedTextPrompt, setShowSelectedTextPrompt] = useState(false);
  const [error, setError] = useState(null);

  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatPanelRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Listen for text selection
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 10 && text.length < 2000) {
        setSelectedText(text);
        setShowSelectedTextPrompt(true);

        // Auto-hide prompt after 5 seconds
        setTimeout(() => {
          setShowSelectedTextPrompt(false);
        }, 5000);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  // Close chat when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        isOpen &&
        chatPanelRef.current &&
        !chatPanelRef.current.contains(event.target) &&
        !event.target.closest('.rag-chat-bubble')
      ) {
        // Don't close if user is selecting text
        const selection = window.getSelection();
        if (selection?.toString().trim()) return;

        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  /**
   * Send a normal question to the RAG backend
   */
  const sendQuestion = async (question) => {
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: question,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.answer || data.response || 'No answer received.',
        sources: data.sources || data.results || [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (err) {
      console.error('RAG query error:', err);
      setError('Failed to get response. Is the backend running?');

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I could not connect to the knowledge base. Please ensure the backend is running.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Send a selected-text context question
   */
  const sendSelectedTextQuestion = async (question) => {
    if (!selectedText || !question.trim()) return;

    setIsLoading(true);
    setError(null);
    setShowSelectedTextPrompt(false);

    // Add user message with context indicator
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question,
      context: selectedText.substring(0, 200) + (selectedText.length > 200 ? '...' : ''),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    try {
      const response = await fetch(`${API_BASE_URL}/query-selected-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selected_text: selectedText,
          question: question,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.answer || data.response || 'No answer received.',
        sources: data.sources || data.results || [],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (err) {
      console.error('RAG selected-text query error:', err);
      setError('Failed to get response.');

      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I could not process your question about the selected text.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedText('');
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedText && showSelectedTextPrompt) {
      sendSelectedTextQuestion(inputValue);
    } else {
      sendQuestion(inputValue);
    }
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  /**
   * Clear chat history
   */
  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  /**
   * Ask about selected text
   */
  const askAboutSelection = () => {
    setIsOpen(true);
    setShowSelectedTextPrompt(true);
    if (inputRef.current) {
      inputRef.current.focus();
      inputRef.current.placeholder = `Ask about: "${selectedText.substring(0, 50)}..."`;
    }
  };

  return (
    <>
      {/* Selected Text Prompt Tooltip */}
      {showSelectedTextPrompt && selectedText && !isOpen && (
        <div className="rag-selection-tooltip">
          <button
            onClick={askAboutSelection}
            className="rag-selection-button"
          >
            <span className="rag-icon-ask">?</span>
            Ask about selection
          </button>
        </div>
      )}

      {/* Chat Bubble Button */}
      <button
        className={`rag-chat-bubble ${isOpen ? 'rag-chat-bubble--open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chat' : 'Open chat assistant'}
        title="Ask the AI Assistant"
      >
        {isOpen ? (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
            <circle cx="8" cy="10" r="1.5"/>
            <circle cx="12" cy="10" r="1.5"/>
            <circle cx="16" cy="10" r="1.5"/>
          </svg>
        )}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div
          ref={chatPanelRef}
          className="rag-chat-panel"
          onKeyDown={handleKeyDown}
        >
          {/* Header */}
          <div className="rag-chat-header">
            <div className="rag-chat-header-title">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span>Book Assistant</span>
            </div>
            <div className="rag-chat-header-actions">
              <button
                onClick={clearChat}
                className="rag-header-button"
                title="Clear chat"
                aria-label="Clear chat history"
              >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="rag-header-button"
                title="Close"
                aria-label="Close chat"
              >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="rag-chat-messages">
            {messages.length === 0 ? (
              <div className="rag-chat-welcome">
                <div className="rag-welcome-icon">
                  <svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                  </svg>
                </div>
                <h3>Welcome!</h3>
                <p>Ask me anything about Physical AI, ROS 2, Simulation, NVIDIA Isaac, or VLA models.</p>
                <div className="rag-suggestions">
                  <button onClick={() => sendQuestion('What is ROS 2?')}>
                    What is ROS 2?
                  </button>
                  <button onClick={() => sendQuestion('How do I set up Gazebo?')}>
                    How do I set up Gazebo?
                  </button>
                  <button onClick={() => sendQuestion('Explain VLA architectures')}>
                    Explain VLA architectures
                  </button>
                </div>
                <p className="rag-tip">
                  <strong>Tip:</strong> Select text on any page, then click "Ask about selection" to get contextual help!
                </p>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`rag-message rag-message--${msg.type}`}
                  >
                    {msg.type === 'user' && (
                      <div className="rag-message-content">
                        <p>{msg.content}</p>
                        {msg.context && (
                          <div className="rag-message-context">
                            <small>Context: "{msg.context}"</small>
                          </div>
                        )}
                      </div>
                    )}

                    {msg.type === 'assistant' && (
                      <div className="rag-message-content">
                        <p>{msg.content}</p>
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="rag-sources">
                            <div className="rag-sources-header">
                              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                                <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                              </svg>
                              <span>Sources</span>
                            </div>
                            <ul>
                              {msg.sources.slice(0, 3).map((source, idx) => (
                                <li key={idx}>
                                  <strong>{source.title || source.payload?.title || 'Source'}</strong>
                                  {(source.module || source.payload?.module) && (
                                    <span className="rag-source-module">
                                      {source.module || source.payload?.module}
                                    </span>
                                  )}
                                  {(source.content || source.payload?.content) && (
                                    <p className="rag-source-snippet">
                                      {(source.content || source.payload?.content).substring(0, 120)}...
                                    </p>
                                  )}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {msg.type === 'error' && (
                      <div className="rag-message-content rag-message-error">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                        </svg>
                        <p>{msg.content}</p>
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}

            {isLoading && (
              <div className="rag-message rag-message--assistant rag-message--loading">
                <div className="rag-loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          {/* Selected Text Indicator */}
          {showSelectedTextPrompt && selectedText && (
            <div className="rag-selected-text-bar">
              <span>Asking about: "{selectedText.substring(0, 50)}..."</span>
              <button onClick={() => {
                setSelectedText('');
                setShowSelectedTextPrompt(false);
              }}>
                <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
          )}

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="rag-chat-input-form">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={showSelectedTextPrompt && selectedText
                ? "Ask about the selected text..."
                : "Ask a question about the book..."}
              disabled={isLoading}
              className="rag-chat-input"
              aria-label="Chat input"
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="rag-chat-submit"
              aria-label="Send message"
            >
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </form>

          {/* Footer */}
          <div className="rag-chat-footer">
            <span>Powered by RAG</span>
            <span className="rag-footer-dot">•</span>
            <span>Physical AI Book</span>
          </div>
        </div>
      )}
    </>
  );
}
