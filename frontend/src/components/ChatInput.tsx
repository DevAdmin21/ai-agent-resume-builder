import { useState } from 'react';

interface Props {
  onSend: (text: string) => void;
  isLoading: boolean;
}

export const ChatInput = ({ onSend, isLoading }: Props) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto p-4 flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Escribe un mensaje..."
        className="flex-1 p-3 border border-borderLight rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-all shadow-sm"
      />
      <button
        disabled={isLoading}
        className="bg-black text-white px-6 py-2 rounded-lg hover:bg-gray-800 disabled:bg-gray-300 transition-colors"
      >
        {isLoading ? '...' : 'Enviar'}
      </button>
    </form>
  );
};