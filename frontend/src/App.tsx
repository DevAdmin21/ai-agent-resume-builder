import { useState } from 'react';
import type { Message } from './api/api';
import { fetchAIResponse } from './api/api';
import { ChatContainer } from './components/ChatContainer';
import { ChatInput } from './components/ChatInput';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    // 1. Crear y agregar el mensaje del usuario al historial
    const userMsg: Message = { role: 'user', content };
    const updatedMessages = [...messages, userMsg];
    
    setMessages(updatedMessages);
    setLoading(true);

    try {
      // 2. Llamar a la API (ahora devuelve un objeto { text, url })
      const aiResult = await fetchAIResponse(updatedMessages);
      
      // 3. Crear el mensaje de la IA incluyendo la URL si existe
      const aiMsg: Message = { 
        role: 'assistant', 
        content: aiResult.text, 
        url: aiResult.url 
      };

      setMessages([...updatedMessages, aiMsg]);
    } catch (error) {
      // Manejo de error básico en la UI
      const errorMsg: Message = { 
        role: 'assistant', 
        content: "Lo siento, ocurrió un error al procesar tu solicitud." 
      };
      setMessages([...updatedMessages, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-chatBg font-sans">
      {/* Header Minimalista */}
      <header className="p-4 border-b border-borderLight flex justify-between items-center bg-white z-10">
        <h1 className="text-sm font-semibold text-gray-700 tracking-tight">
          AI Agent Resume Builder
        </h1>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-400 uppercase tracking-widest">En línea</span>
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        </div>
      </header>

      {/* Contenedor de mensajes (Lógica de scroll integrada) */}
      <ChatContainer messages={messages} />

      {/* Footer con el input */}
      <footer className="border-t border-borderLight bg-white py-4 shadow-[0_-4px_12px_rgba(0,0,0,0.02)]">
        <ChatInput onSend={handleSendMessage} isLoading={loading} />
      </footer>
    </div>
  );
}

export default App;