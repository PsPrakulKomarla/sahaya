"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { UserMessage } from "./user-message";
import { AIMessage } from "./ai-message";
import { TypingIndicator } from "./typing-indicator";
import { SuggestedReplies } from "./suggested-replies";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Paperclip, Mic } from "lucide-react";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ConversationPanelProps {
  className?: string;
}

const mockMessages: Message[] = [
  {
    id: "1",
    role: "user",
    content: "I need to apply for an Income Certificate for my daughter's college admission.",
    timestamp: "10:30 AM",
  },
  {
    id: "2",
    role: "assistant",
    content: "I'll help you apply for an Income Certificate. Let me find the right government portal for this service. I'm checking the Karnataka Revenue Department website now.",
    timestamp: "10:31 AM",
  },
  {
    id: "3",
    role: "user",
    content: "She needs it by next Friday. Is that possible?",
    timestamp: "10:32 AM",
  },
  {
    id: "4",
    role: "assistant",
    content: "I'll do my best to expedite the process. The standard processing time is 3-5 working days, so next Friday should be achievable if we submit today. Let me check the eligibility requirements first — you'll need your Aadhaar card, salary slips for the last 3 months, and a self-declaration form.",
    timestamp: "10:33 AM",
  },
];

const suggestedReplies = [
  "I have all my documents ready",
  "What documents do I need?",
  "How long will this take?",
  "Can you check my eligibility?",
];

export function ConversationPanel({ className }: ConversationPanelProps) {
  const [messages, setMessages] = React.useState<Message[]>(mockMessages);
  const [inputValue, setInputValue] = React.useState("");
  const [isTyping, setIsTyping] = React.useState(false);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      }),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue("");
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "I'm processing your request. Let me navigate to the official portal and check the current status of your application requirements.",
        timestamp: new Date().toLocaleTimeString("en-US", {
          hour: "numeric",
          minute: "2-digit",
          hour12: true,
        }),
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 2000);
  };

  const handleSuggestionSelect = (suggestion: string) => {
    setInputValue(suggestion);
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) =>
          message.role === "user" ? (
            <UserMessage
              key={message.id}
              content={message.content}
              timestamp={message.timestamp}
            />
          ) : (
            <AIMessage
              key={message.id}
              content={message.content}
              timestamp={message.timestamp}
            />
          )
        )}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Replies */}
      <div className="px-4 pb-2">
        <SuggestedReplies
          suggestions={suggestedReplies}
          onSelect={handleSuggestionSelect}
        />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" aria-label="Attach file">
            <Paperclip className="h-5 w-5 text-slate-400" />
          </Button>
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Describe what you need help with..."
            className="flex-1"
            aria-label="Message input"
          />
          <Button variant="ghost" size="icon" aria-label="Voice input">
            <Mic className="h-5 w-5 text-slate-400" />
          </Button>
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!inputValue.trim()}
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
