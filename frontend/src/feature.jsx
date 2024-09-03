// App.js
import React, { useState, useRef, useEffect } from 'react';
import { File, Camera, Pencil, Clock, ChevronRight, Book } from 'lucide-react';
import { getGeminiResponse } from './geminiApi';

const Header = () => (
  <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#e0e0e0] px-10 py-3 bg-[#FF9933]">
    <div className="flex items-center gap-4 text-white">
      <div className="size-12">
        <img
          src="/Ministry_of_Law_and_Justice.svg"
          alt="JusticeBharat logo"
          className="h-10 "
        />
      </div>
      <h2 className="text-white text-2xl font-bold leading-tight tracking-[-0.015em]">Government of India Legal Consultation</h2>
    </div>
    <div className="flex flex-1 justify-end gap-8">
      <div className="flex items-center gap-9">
        {['Home', 'Services', 'Technology', 'About Us', 'Contact Us'].map((item) => (
          <a key={item} className="text-white text-sm font-medium leading-normal hover:underline" href="#">
            {item}
          </a>
        ))}
      </div>
      <div className="flex gap-2">
        <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 px-4 bg-[#138808] text-white text-sm font-bold leading-normal tracking-[0.015em]">
          <span className="truncate">Sign Up</span>
        </button>
        <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 px-4 bg-white text-[#000080] text-sm font-bold leading-normal tracking-[0.015em]">
          <span className="truncate">Log In</span>
        </button>
      </div>
    </div>
  </header>
);

const ChatMessage = ({ sender, time, message }) => (
  <div className={`flex gap-3 p-4 ${sender === 'Legal Assistant' ? 'bg-[#f0f0f0]' : ''}`}>
    <div className="flex flex-1 flex-col items-stretch gap-2">
      <div className="flex flex-col gap-1">
        <div className="flex flex-wrap items-center gap-3">
          <p className="text-[#000080] text-base font-bold leading-tight">{sender}</p>
          <p className="text-gray-500 text-sm font-normal leading-normal">{time}</p>
        </div>
        <p className="text-gray-700 text-base font-normal leading-normal">{message}</p>
      </div>
    </div>
  </div>
);

const ChatInput = ({ onSendMessage, inputValue, setInputValue }) => (
  <div className="flex items-center px-4 py-3 gap-3 @container">
    <label className="flex flex-col min-w-40 h-12 flex-1">
      <div className="flex w-full flex-1 items-stretch rounded-xl h-full">
        <input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type here..."
          className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-gray-800 focus:outline-0 focus:ring-0 border-none bg-gray-100 focus:border-none h-full placeholder:text-gray-500 px-4 rounded-r-none border-r-0 pr-2 text-base font-normal leading-normal"
        />
        <div className="flex border-none bg-gray-100 items-center justify-center pr-4 rounded-r-xl border-l-0 !pr-2">
          <button
            onClick={onSendMessage}
            className="text-blue rounded-full p-2 hover:bg-[#0000A0]"
          >
            Send
          </button>
        </div>
      </div>
    </label>
  </div>
);

const ActionButton = ({ icon: Icon, text, onClick }) => (
  <button
    onClick={onClick}
    className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 px-4 flex-1 bg-[#F0F0F0] text-[#000080] gap-2 pl-4 text-sm font-bold leading-normal tracking-[0.015em] hover:bg-[#E0E0E0]"
  >
    <Icon className="text-[#000080]" size={20} />
    <span className="truncate">{text}</span>
  </button>
);

const FeatureItem = ({ icon: Icon, title, description }) => (
  <div className="flex items-center gap-4 bg-white px-4 min-h-[72px] py-2 justify-between border-b border-gray-200 hover:bg-[#F0F0F0]">
    <div className="flex items-center gap-4">
      <div className="text-[#000080] flex items-center justify-center rounded-lg bg-[#F0F0F0] shrink-0 size-12">
        <Icon size={24} />
      </div>
      <div className="flex flex-col justify-center">
        <p className="text-[#000080] text-base font-medium leading-normal line-clamp-1">{title}</p>
        <p className="text-gray-500 text-sm font-normal leading-normal line-clamp-2">{description}</p>
      </div>
    </div>
    <div className="shrink-0">
      <div className="text-[#000080] flex size-7 items-center justify-center">
        <ChevronRight size={24} />
      </div>
    </div>
  </div>
);

const App = () => {
  const [messages, setMessages] = useState([
    { sender: 'Legal Assistant', time: '2:30 PM', message: 'Welcome to Government of India Legal Consultation! How can I assist you today?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (inputValue.trim() !== '') {
      const newMessage = { sender: 'You', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), message: inputValue };
      setMessages([...messages, newMessage]);
      setInputValue('');
      setIsLoading(true);

      try {
        const response = await getGeminiResponse(inputValue);
        
        const assistantMessage = { 
          sender: 'Legal Assistant', 
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), 
          message: response 
        };
        setMessages(prevMessages => [...prevMessages, assistantMessage]);
      } catch (error) {
        console.error('Error getting response from Gemini AI:', error);
        const errorMessage = { 
          sender: 'Legal Assistant', 
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), 
          message: 'I apologize, but I encountered an error while processing your request. Please try again later.' 
        };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleActionButton = (action) => {
    const actionMessage = `[${action} attached]`;
    setInputValue(prevValue => prevValue + ' ' + actionMessage);
  };

  return (
    <div className="relative flex size-full min-h-screen flex-col bg-white overflow-x-hidden" style={{ fontFamily: 'Inter, "Noto Sans", sans-serif' }}>
      <div className="layout-container flex h-full grow flex-col">
        <Header />
        <div className="flex flex-1 py-5">
          <div className="w-1/4 border-r border-gray-200">
            <FeatureItem icon={Pencil} title="Note maker" description="Create and manage notes" />
            <FeatureItem icon={Clock} title="Chat history" description="View past conversations" />
            <FeatureItem icon={Book} title="Legal resources" description="Access legal documents and acts" />
          </div>
          <div className="layout-content-container flex flex-col w-3/4 px-10">
            <div className="flex flex-wrap justify-between gap-3 p-4">
              <p className="text-[#000080] tracking-light text-[32px] font-bold leading-tight min-w-72">Chat with Legal Assistant </p>
            </div>
            <div className="flex-grow overflow-y-auto mb-4 bg-white rounded-lg shadow-md">
              {messages.map((msg, index) => (
                <ChatMessage key={index} sender={msg.sender} time={msg.time} message={msg.message} />
              ))}
              {isLoading && (
                <div className="flex justify-center items-center p-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#000080]"></div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            <ChatInput onSendMessage={handleSendMessage} inputValue={inputValue} setInputValue={setInputValue} />
            <div className="flex gap-2 mt-4">
              <ActionButton icon={File} text="File" onClick={() => handleActionButton('File')} />
              <ActionButton icon={Camera} text="Photo" onClick={() => handleActionButton('Photo')} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;

