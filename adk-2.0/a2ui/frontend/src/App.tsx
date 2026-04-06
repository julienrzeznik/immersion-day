import React, { useState, useEffect } from 'react';
import './App.css';
import { A2UIProvider, A2UIRenderer, useA2UIActions, useA2UI, initializeDefaultCatalog } from '@a2ui/react';

initializeDefaultCatalog();

interface Message {
  role: 'user' | 'assistant';
  content: string;
  a2uiData?: any;
}

function ChatContent() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [contextId, setContextId] = useState<string | null>(null);
  const [isA2UILoading, setIsA2UILoading] = useState(false);
  const { processMessages, clearSurfaces } = useA2UIActions();
  const { getSurfaces } = useA2UI();

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsA2UILoading(true);

    try {
      const response = await fetch('http://localhost:8502/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'message/stream',
          params: {
            contextId: contextId,
            message: {
              messageId: `msg-${Date.now()}`,
              role: 'user',
              parts: [{ kind: 'text', text: input }],
            },
          },
          id: 1,
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let assistantMessage = '';

      if (reader) {
        // Add an empty assistant message to update
        setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

        while (true) {
          const { done, value } = await reader.read();
          buffer += decoder.decode(value, { stream: !done });
          
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep the last incomplete line
          
          for (const line of lines) {
            let trimmedLine = line.trim();
            if (!trimmedLine) continue;
            
            const jsonStart = trimmedLine.indexOf('{');
            if (jsonStart !== -1) {
              trimmedLine = trimmedLine.substring(jsonStart);
            }
            
            try {
              const parsed = JSON.parse(trimmedLine);
              console.log('Parsed streaming event:', parsed);
              
              const newContextId = parsed.result?.contextId;
              if (newContextId) {
                setContextId(newContextId);
              }
              
              // In A2A, updates usually come in parsed.result or parsed.params
              // Let's check for result.output which we sent in __main__.py
              const output = parsed.result?.output || 
                             parsed.params?.message?.parts?.[0]?.text ||
                             parsed.result?.status?.message?.parts?.[0]?.text;
              
              if (output) {
                try {
                  // Try to parse output as AgentResponse
                  const parsedOutput = JSON.parse(output);
                  if (parsedOutput && typeof parsedOutput === 'object' && 'text_response' in parsedOutput) {
                    assistantMessage = parsedOutput.text_response;
                    setMessages((prev) => {
                      const newMessages = [...prev];
                      newMessages[newMessages.length - 1] = { role: 'assistant', content: assistantMessage };
                      return newMessages;
                    });
                    if (parsedOutput.ui_payload) {
                      console.log('A2UI Data from structured output:', parsedOutput.ui_payload);
                      clearSurfaces();
                      processMessages(Array.isArray(parsedOutput.ui_payload) ? parsedOutput.ui_payload : [parsedOutput.ui_payload]);
                    }
                  } else {
                    assistantMessage += output;
                    setMessages((prev) => {
                      const newMessages = [...prev];
                      newMessages[newMessages.length - 1] = { role: 'assistant', content: assistantMessage };
                      return newMessages;
                    });
                  }
                } catch (e) {
                   // Not JSON at root, try to find <a2ui-json> tags
                   let tempOutput = output;
                   let startIdx = tempOutput.indexOf('<a2ui-json>');
                   let foundTags = false;
                   
                   // Clear surfaces before processing tags if we find any tags
                   if (startIdx !== -1) {
                     clearSurfaces();
                   }
                   
                   while (startIdx !== -1) {
                     const endIdx = tempOutput.indexOf('</a2ui-json>');
                     if (endIdx !== -1) {
                       foundTags = true;
                       const jsonStr = tempOutput.substring(startIdx + 11, endIdx).trim();
                       try {
                         const parsedTags = JSON.parse(jsonStr);
                         console.log('A2UI Data from tags:', parsedTags);
                         processMessages(Array.isArray(parsedTags) ? parsedTags : [parsedTags]);
                       } catch (err) {
                         console.error('Failed to parse JSON inside tags:', err);
                       }
                       tempOutput = tempOutput.substring(endIdx + 12);
                       startIdx = tempOutput.indexOf('<a2ui-json>');
                     } else {
                       break; // No closing tag
                     }
                   }
                   
                   if (foundTags) {
                     // Update text content to remove tags
                     assistantMessage = output.replace(/<a2ui-json>.*?<\/a2ui-json>/gs, '').trim();
                     setMessages((prev) => {
                       const newMessages = [...prev];
                       newMessages[newMessages.length - 1] = { role: 'assistant', content: assistantMessage };
                       return newMessages;
                     });
                   } else {
                     // No tags, just text
                     assistantMessage = output;
                     setMessages((prev) => {
                       const newMessages = [...prev];
                       newMessages[newMessages.length - 1] = { role: 'assistant', content: assistantMessage };
                       return newMessages;
                     });
                   }
                }
              }
            } catch (e) {
              console.error('Failed to parse line', e);
            }
          }
          
          if (done) {
            setIsA2UILoading(false);
            break;
          }
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setIsA2UILoading(false);
    }
  };

  const surfaces = getSurfaces();
  const surfaceEntries = Array.from(surfaces.entries());

  return (
    <div className="App" style={{ 
      display: 'flex', 
      gap: '20px', 
      padding: '20px', 
      fontFamily: "'Outfit', 'Inter', sans-serif", 
      height: 'calc(100vh - 40px)', 
      boxSizing: 'border-box',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      borderRadius: '16px',
    }}>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .chat-window::-webkit-scrollbar {
          width: 6px;
        }
        .chat-window::-webkit-scrollbar-thumb {
          background-color: rgba(0, 0, 0, 0.1);
          border-radius: 3px;
        }
        
        .message {
          animation: fadeIn 0.3s ease-in-out;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      
      {/* Left side: Chat */}
      <div className="chat-container" style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        height: '100%',
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        border: '1px solid rgba(255, 255, 255, 0.18)',
      }}>
        <h1 style={{ 
          fontSize: '24px', 
          fontWeight: 700, 
          marginBottom: '20px',
          background: 'linear-gradient(45deg, #007bff, #00c6ff)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textAlign: 'center'
        }}>A2UI Medical Assistant</h1>
        
        <div className="chat-window" style={{ 
          flex: 1, 
          overflowY: 'auto', 
          background: 'rgba(245, 247, 250, 0.5)',
          borderRadius: '12px',
          padding: '15px',
          marginBottom: '15px',
        }}>
          {messages.map((msg, i) => {
            // Skip function calls in display
            if (msg.content.startsWith('function_calls=')) return null;
            
            return (
              <div key={i} className={`message ${msg.role}`} style={{ 
                marginBottom: '12px', 
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
              }}>
                <div className="content" style={{ 
                  display: 'inline-block', 
                  padding: '10px 16px', 
                  borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px', 
                  background: msg.role === 'user' ? 'linear-gradient(135deg, #007bff 0%, #00c6ff 100%)' : '#fff', 
                  color: msg.role === 'user' ? '#fff' : '#333',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                  maxWidth: '80%',
                  lineHeight: '1.4',
                }}>
                  <div>{msg.content.replace(/<a2ui-json>.*?<\/a2ui-json>/s, '')}</div>
                </div>
              </div>
            );
          })}
        </div>
        
        <div className="input-area" style={{ display: 'flex', gap: '10px' }}>
          <input 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              style={{ 
                flex: 1, 
                padding: '12px 16px', 
                borderRadius: '8px', 
                border: '1px solid #ddd',
                background: '#fff',
                fontSize: '14px',
                outline: 'none',
              }}
              placeholder="Type your message..."
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button onClick={sendMessage} style={{ 
            padding: '0 20px', 
            borderRadius: '8px', 
            border: 'none', 
            background: 'linear-gradient(135deg, #007bff 0%, #00c6ff 100%)', 
            color: '#fff', 
            cursor: 'pointer',
            fontWeight: 600,
          }}>Send</button>
        </div>
      </div>
      
      {/* Right side: A2UI UX */}
      <div className="a2ui-container" style={{ 
        flex: 1, 
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        borderRadius: '16px',
        padding: '20px',
        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        border: '1px solid rgba(255, 255, 255, 0.18)',
        overflowY: 'auto', 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column' 
      }}>
        <h2 style={{ 
          fontSize: '20px', 
          fontWeight: 700, 
          marginBottom: '20px',
          color: '#333',
          textAlign: 'center'
        }}>Generated Interface</h2>
        
        {isA2UILoading && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px', flexDirection: 'column', gap: '10px' }}>
            <div style={{
              border: '4px solid rgba(0, 0, 0, 0.1)',
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              borderLeftColor: '#007bff',
              animation: 'spin 1s linear infinite',
            }} />
            <span style={{ color: '#666', fontSize: '14px' }}>Loading interface...</span>
          </div>
        )}
        
        <div style={{ flex: 1 }}>
          {surfaceEntries.map(([surfaceId]) => (
            <div key={surfaceId} style={{ 
              marginTop: '10px', 
              background: '#fff', 
              padding: '15px', 
              borderRadius: '12px', 
              border: '1px solid #eee',
              boxShadow: '0 4px 6px rgba(0,0,0,0.02)',
            }}>
              <A2UIRenderer surfaceId={surfaceId} />
            </div>
          ))}
          
          {surfaceEntries.length === 0 && !isA2UILoading && (
            <div style={{ color: '#999', textAlign: 'center', marginTop: '50px', fontSize: '14px' }}>
              No interface generated yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <A2UIProvider>
      <ChatContent />
    </A2UIProvider>
  );
}


