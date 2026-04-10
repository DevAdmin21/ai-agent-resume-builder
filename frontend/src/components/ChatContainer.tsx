import { useEffect, useRef } from 'react';
import type { Message } from '../api/api';
import { ChatMessage } from './ChatMessage';

interface Props {
  messages: Message[];
}

export const ChatContainer = ({ messages }: Props) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Efecto para hacer scroll automático al final cuando hay nuevos mensajes
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  return (
    <div 
      ref={scrollRef}
      className="flex-1 overflow-y-auto bg-chatBg scroll-smooth"
    >
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-gray-400">
          <p className="text-lg font-light">¿En qué puedo ayudarte hoy?</p>
        </div>
      ) : (
        <div className="flex flex-col">
          {messages.map((m, idx) => (
            <ChatMessage key={idx} message={m} />
          ))}
        </div>
      )}
    </div>
  );
};