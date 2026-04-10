import type{ Message } from '../api/api';

export const ChatMessage = ({ message }: { message: Message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full py-6 px-4 border-b border-gray-100 ${isUser ? 'bg-gray-50' : 'bg-white'}`}>
      <div className="max-w-3xl mx-auto flex gap-4 w-full">
        <div className={`w-8 h-8 rounded flex items-center justify-center text-white text-xs font-bold shrink-0 ${isUser ? 'bg-indigo-600' : 'bg-emerald-600'}`}>
          {isUser ? 'U' : 'AI'}
        </div>
        
        <div className="flex-1 flex flex-col gap-4">
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>

          {/* Botón de descarga si existe URL */}
          {!isUser && message.url && (
            <a 
              href={message.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 w-fit px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-all shadow-sm"
            >
              Descargar documento
            </a>
          )}
        </div>
      </div>
    </div>
  );
};