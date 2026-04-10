export interface Message {
  role: 'user' | 'assistant';
  content: string;
  url?: string; // Añadimos url opcional
}

export const fetchAIResponse = async (messages: Message[]): Promise<{ text: string, url?: string }> => {
  try {
    const lastUserMessage = messages[messages.length - 1];
    const userText = lastUserMessage ? lastUserMessage.content : "";

    const payload = {
      text: userText,
      generate_document: true,
      document_format: "pdf",
      language: "es"
    };

    const API_URL = "https://ai-agent-resume-builder-production.up.railway.app/api/v1/summarize";

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error(`Error: ${response.status}`);

    const data = await response.json();

    const keyPointsFormatted = data.key_points ? data.key_points.map((point: string) => `• ${point}`).join('\n') : "No se encontraron puntos clave.";
    const fullUrl = `https://ai-agent-resume-builder-production.up.railway.app${data.document_url}`;

    return {
      text: keyPointsFormatted,
      url: fullUrl
    };
  } catch (error) {
    console.error("Error fetching AI response:", error);
    return { text: "Lo siento, hubo un error al procesar tu solicitud." };
  }
};