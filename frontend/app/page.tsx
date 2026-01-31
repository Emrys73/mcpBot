
'use client';

import { useState, FormEvent, useRef, useEffect } from 'react';
import {
  Search,
  MapPin,
  MoreHorizontal,
  ArrowUp,
  LayoutGrid,
  Clock,
  Globe,
  User,
  Bot,
  Copy,
  Check,
  Pencil,
  X,
  Moon,
  Sun
} from 'lucide-react';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';

type Message = {
  role: 'user' | 'ai';
  content: string;
};

// Explicit type for code block props from react-markdown
interface CodeProps {
  node?: any;
  inline?: boolean;
  className?: string;
  children?: React.ReactNode;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [isDeepSearch, setIsDeepSearch] = useState(false);
  const [isReasoning, setIsReasoning] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };


  useEffect(() => {
    if (editingIndex === null) {
      scrollToBottom();
    }
  }, [messages, loading, editingIndex]);

  // Dark Mode Initialization
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);

    if (newMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const startEdit = (index: number, content: string) => {
    setEditingIndex(index);
    setEditContent(content);
  };

  const cancelEdit = () => {
    setEditingIndex(null);
    setEditContent('');
  };

  const saveEdit = async (index: number) => {
    if (!editContent.trim()) return;

    // Truncate history to the point of edit
    const newHistory = messages.slice(0, index);
    const newMessage: Message = { role: 'user', content: editContent };

    setMessages([...newHistory, newMessage]);
    setEditingIndex(null);
    setEditContent('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8002/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: editContent }), // Use the edited content
      });

      const data = await res.json();

      // Add AI response
      setMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    } catch (error) {
      console.error('Error fetching chat:', error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I encountered an error. Is the backend running?' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add user message
    const userMsg: Message = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    const currentQuery = query;
    setQuery(''); // Clear input
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8002/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: currentQuery }),
      });

      const data = await res.json();

      // Add AI response
      setMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    } catch (error) {
      console.error('Error fetching chat:', error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I encountered an error. Is the backend running?' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#F3F3F2] dark:bg-[#171717] text-gray-900 dark:text-gray-100 font-sans overflow-hidden transition-colors">
      {/* Sidebar */}
      <aside className="w-16 flex-shrink-0 flex flex-col items-center py-6 border-r border-[#E5E5E5] dark:border-gray-800 bg-[#F9F9F9] dark:bg-[#121212] transition-colors">
        <div className="mb-8">
          <div className="w-8 h-8 bg-black rounded-md flex items-center justify-center text-white font-bold">
            +
          </div>
        </div>

        <nav className="flex flex-col gap-6 text-gray-500">
          <button className="hover:text-black hover:bg-gray-200 p-2 rounded-lg transition-colors">
            <Search size={24} />
          </button>
          <button className="hover:text-black hover:bg-gray-200 p-2 rounded-lg transition-colors">
            <Globe size={24} />
          </button>
          <button className="hover:text-black hover:bg-gray-200 p-2 rounded-lg transition-colors">
            <LayoutGrid size={24} />
          </button>
          <button className="hover:text-black hover:bg-gray-200 p-2 rounded-lg transition-colors">
            <Clock size={24} />
          </button>
          <button
            onClick={toggleTheme}
            className="hover:text-black hover:bg-gray-200 p-2 rounded-lg transition-colors"
            title="Toggle Dark Mode"
          >
            {isDarkMode ? <Sun size={24} /> : <Moon size={24} />}
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative h-full bg-[#F3F3F2] dark:bg-[#171717] transition-colors">

        {/* Top Right Controls */}
        <div className="absolute top-6 right-6 z-10 flex items-center gap-4">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-300 to-gray-400"></div>
          <button className="bg-black text-white px-4 py-2 rounded-full text-sm font-medium">
            Get Pro
          </button>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto px-4 py-8 custom-scrollbar">
          <div className="max-w-3xl mx-auto space-y-6 pb-32">

            {/* Initial Greeting if no messages */}
            {messages.length === 0 && (
              <div className="text-center mt-20 mb-10">
                <h1 className="text-4xl font-semibold tracking-tight text-[#1A1A1A] dark:text-gray-100 transition-colors">
                  What can I help with?
                </h1>
              </div>
            )}

            {/* Message List */}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={clsx(
                  "flex gap-4 w-full group",
                  msg.role === 'user' ? "justify-end" : "justify-start"
                )}
              >
                {msg.role === 'ai' && (
                  <div className="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white flex-shrink-0 mt-1">
                    <Bot size={16} />
                  </div>
                )}

                {/* User Actions - Left Side */}
                {msg.role === 'user' && editingIndex !== idx && (
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2 self-center">
                    <button
                      onClick={() => startEdit(idx, msg.content)}
                      className="p-2 rounded-full text-gray-400 hover:text-black hover:bg-gray-200 transition-colors"
                      title="Edit"
                    >
                      <Pencil size={16} />
                    </button>
                    <button
                      onClick={() => handleCopy(msg.content, idx)}
                      className="p-2 rounded-full text-gray-400 hover:text-black hover:bg-gray-200 transition-colors"
                      title="Copy"
                    >
                      {copiedIndex === idx ? <Check size={16} /> : <Copy size={16} />}
                    </button>
                  </div>
                )}

                <div className={clsx(
                  "px-5 py-3.5 rounded-2xl max-w-[75%] leading-relaxed overflow-x-auto transition-colors",
                  msg.role === 'user'
                    ? "bg-[#F3F3F2] dark:bg-[#262626] text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-800"
                    : "bg-white dark:bg-[#1e1e1e] text-gray-800 dark:text-gray-100 shadow-sm border border-gray-100 dark:border-gray-800"
                )}>
                  {editingIndex === idx ? (
                    <div className="w-full">
                      <textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        className="w-full bg-white p-2 text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black mb-2 resize-none"
                        rows={3}
                        autoFocus
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={cancelEdit}
                          className="p-1 rounded-full bg-gray-200 hover:bg-gray-300 text-gray-600 transition-colors"
                          title="Cancel"
                        >
                          <X size={16} />
                        </button>
                        <button
                          onClick={() => saveEdit(idx)}
                          className="p-1 rounded-full bg-black text-white hover:bg-gray-800 transition-colors"
                          title="Save & Restart"
                        >
                          <ArrowUp size={16} />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      {msg.role === 'ai' ? (
                        <div className="prose prose-sm max-w-none text-gray-800 dark:text-gray-100 dark:prose-invert break-words">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              table({ node, className, children, ...props }) {
                                return (
                                  <div className="overflow-x-auto my-4 w-full">
                                    <table className="border-collapse border border-gray-300 dark:border-gray-700 w-full rounded-lg overflow-hidden" {...props}>
                                      {children}
                                    </table>
                                  </div>
                                );
                              },
                              thead({ node, className, children, ...props }) {
                                return <thead className="bg-gray-100 dark:bg-gray-800" {...props}>{children}</thead>;
                              },
                              tr({ node, className, children, ...props }) {
                                return <tr className="border-b border-gray-300 dark:border-gray-700 last:border-b-0" {...props}>{children}</tr>;
                              },
                              th({ node, className, children, ...props }) {
                                return <th className="border border-gray-300 dark:border-gray-700 px-4 py-2 text-left font-semibold text-sm" {...props}>{children}</th>;
                              },
                              td({ node, className, children, ...props }) {
                                return <td className="border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm" {...props}>{children}</td>;
                              },
                              code({ node, inline, className, children, ...props }: CodeProps) {
                                const match = /language-(\w+)/.exec(className || '')
                                return !inline && match ? (
                                  <SyntaxHighlighter
                                    {...props}
                                    style={dracula}
                                    language={match[1]}
                                    PreTag="div"
                                    className="rounded-md my-2"
                                  >
                                    {String(children).replace(/\n$/, '')}
                                  </SyntaxHighlighter>
                                ) : (
                                  <code {...props} className={clsx("bg-gray-100 dark:bg-gray-800 rounded px-1 py-0.5 text-sm", className)}>
                                    {children}
                                  </code>
                                )
                              }
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      )}
                    </>
                  )}
                </div>

                {/* AI Actions - Right Side */}
                {msg.role === 'ai' && (
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2 self-end pb-2">
                    <button
                      onClick={() => handleCopy(msg.content, idx)}
                      className="p-2 rounded-full text-gray-400 hover:text-black hover:bg-gray-200 transition-colors"
                      title="Copy"
                    >
                      {copiedIndex === idx ? <Check size={16} /> : <Copy size={16} />}
                    </button>
                  </div>
                )}

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 flex-shrink-0 mt-1">
                    <User size={16} />
                  </div>
                )}
              </div>
            ))}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex gap-4 w-full justify-start">
                <div className="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white flex-shrink-0 mt-1">
                  <Bot size={16} />
                </div>
                <div className="bg-white px-5 py-4 rounded-2xl shadow-sm border border-gray-100">
                  <div className="flex items-center gap-2 text-gray-400">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area (Fixed Bottom) */}
        <div className="w-full bg-[#F3F3F2] dark:bg-[#171717] p-4 absolute bottom-0 transition-colors">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="w-full relative group">
              <div className="relative bg-white dark:bg-[#262626] rounded-[32px] shadow-sm border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-all focus-within:shadow-md focus-within:border-gray-300 dark:focus-within:border-gray-500 p-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={messages.length > 0 ? "Reply..." : "Ask anything..."}
                  className="w-full h-14 pl-4 pr-12 bg-transparent outline-none text-lg text-gray-800 dark:text-gray-100 placeholder:text-gray-400"
                />

                <div className="flex items-center justify-between px-2 pb-2 mt-2">
                  <div className="flex items-center gap-2">
                    {/* Icons... */}
                    <button type="button" className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-50 transition-colors">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" /></svg>
                    </button>

                    <button
                      type="button"
                      onClick={() => setIsDeepSearch(!isDeepSearch)}
                      className={clsx(
                        "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors",
                        isDeepSearch
                          ? "bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800"
                          : "bg-white dark:bg-[#333] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-[#444]"
                      )}
                    >
                      <Globe size={14} />
                      Deep Search
                    </button>

                    <button
                      type="button"
                      onClick={() => setIsReasoning(!isReasoning)}
                      className={clsx(
                        "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors",
                        isReasoning
                          ? "bg-amber-50 dark:bg-amber-900/30 text-amber-900 dark:text-amber-400 border-amber-200 dark:border-amber-800"
                          : "bg-white dark:bg-[#333] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-[#444]"
                      )}
                    >
                      <MapPin size={14} />
                      Reason
                    </button>
                  </div>

                  <button
                    type="submit"
                    disabled={!query.trim()}
                    className={clsx(
                      "p-2 rounded-full transition-all duration-200",
                      query.trim()
                        ? "bg-black dark:bg-white text-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-200"
                        : "bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
                    )}
                  >
                    <ArrowUp size={20} />
                  </button>
                </div>
              </div>
            </form>
            <div className="text-center text-xs text-gray-400 mt-2 pb-2">
              AI can make mistakes. Please double-check responses.
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
