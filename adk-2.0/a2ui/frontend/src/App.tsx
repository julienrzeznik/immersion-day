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
  const { processMessages, clearSurfaces } = useA2UIActions();
  const { getSurfaces } = useA2UI();

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

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
                     assistantMessage += output;
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
          
          if (done) break;
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const surfaces = getSurfaces();
  const surfaceEntries = Array.from(surfaces.entries());

  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Inter, sans-serif' }}>
      <h1>A2UI Medical Assistant</h1>
      <div className="chat-window" style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '10px', height: '400px', overflowY: 'auto', background: '#f9f9f9' }}>
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`} style={{ marginBottom: '10px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
            <div className="content" style={{ display: 'inline-block', padding: '8px 12px', borderRadius: '12px', background: msg.role === 'user' ? '#007bff' : '#e9ecef', color: msg.role === 'user' ? '#fff' : '#000' }}>
              <div>{msg.content.replace(/<a2ui-json>.*?<\/a2ui-json>/s, '')}</div>
            </div>
          </div>
        ))}
        
        {/* Render surfaces at the bottom of the chat */}
        {surfaceEntries.map(([surfaceId]) => (
          <div key={surfaceId} style={{ marginTop: '10px', background: '#fff', padding: '10px', borderRadius: '8px', border: '1px solid #ddd' }}>
            <A2UIRenderer surfaceId={surfaceId} />
          </div>
        ))}
      </div>
      <div className="input-area" style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
        <input 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
            placeholder="Type your message..."
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage} style={{ padding: '8px 16px', borderRadius: '4px', border: 'none', background: '#007bff', color: '#fff', cursor: 'pointer' }}>Send</button>
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


