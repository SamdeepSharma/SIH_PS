// geminiApi.js

const API_KEY = 'AIzaSyDNn20lE_kpgrUtLptZjkbOBSLjWCpWrrw'; // Replace with your actual Gemini API key
const API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

let conversationHistory = [];

export const getGeminiResponse = async (prompt) => {
  try {
    // Add user's message to conversation history
    conversationHistory.push({ role: "user", parts: [{ text: prompt }] });

    const response = await fetch(`${API_URL}?key=${API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: conversationHistory,
        generationConfig: {
          temperature: 1,
          topP: 0.95,
          topK: 64,
          maxOutputTokens: 8192,
        },
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to get response from Gemini AI');
    }

    const data = await response.json();
    const aiResponse = data.candidates[0].content.parts[0].text;

    // Add AI's response to conversation history
    conversationHistory.push({ role: "model", parts: [{ text: aiResponse }] });

    // Format the AI response into point form
    const formattedResponse = formatToPoints(aiResponse);

    return formattedResponse;
  } catch (error) {
    console.error('Error in getGeminiResponse:', error);
    throw error;
  }
};

// Helper function to reset conversation history
export const resetConversation = () => {
  conversationHistory = [];
};

// Helper function to format text into point form
const formatToPoints = (text) => {
  // Split the text into sentences
  const sentences = text.split(/(?<=[.!?])\s+/);
  
  // Filter out empty sentences and format each as a bullet point
  const points = sentences
    .map(sentence => sentence.trim())
    .filter(sentence => sentence.length > 0)
    .map(sentence => {
      // Make words after "import" bold
      const boldImports = sentence.replace(/\bimport\s+(\w+)/g, 'import **$1**');
      return `• ${boldImports}`;
    });

  // Join the bullet points with double newlines for extra spacing
  return points.join('\n\n');
};