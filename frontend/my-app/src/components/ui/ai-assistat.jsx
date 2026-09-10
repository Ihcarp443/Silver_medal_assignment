import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles, X, Loader2 ,Mic, Square, Trash,NotebookPen  , PlusCircleIcon ,Volume2,Paperclip} from "lucide-react";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatSkeleton } from "./ChatSkelton";
import TextType from "./TextType";
import { Component } from "./profileDropdown";
import { Image as ImageIcon, Camera } from "lucide-react";
import {
  ThumbsUp,
  ThumbsDown,
  Copy,
  RotateCcw,
} from "lucide-react";
import { Toaster } from "@/components/ui/sonner";
import Image from "next/image";


const AIMessageBar = () => {
  const BASE_URL = process.env.NEXT_PUBLIC_ENDPOINT || "http://50.19.164.128:8000";
  const BASE_URL_2 = process.env.NEXT_PUBLIC_ENDPOINT_2;
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const[threadID,set_threadID]=useState("")
  const [isSpeaking, setIsSpeaking] = useState(false);
  const fileInputRef = useRef(null);
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] =useState(null);
  const[loadPastChat,setloadPastChat]=useState(false)
  const[user_id,setuserId]=useState("")
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [feedbackReason, setFeedbackReason] = useState("");
  const [customReason, setCustomReason] = useState("");
  const reasons = [
  "Too long",
  "Too short",
  "Hard to understand",
  "Other"
];

  const regenerateAnswer = async () => {
    setMessages(prev => [
  ...prev,
  {
    text: `**Feedback**: ${feedbackReason}${
      customReason ? ` - ${customReason}` : ""
    }`,
    isUser: true,
    isFeedback: true
  }
]);
  setShowFeedbackModal(false);
  try {
    setIsTyping(true)
    const response = await fetch(`${BASE_URL}/feedback/improve`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: selectedMessage?.question || "",
        answer: selectedMessage?.text || "",
        reason: feedbackReason,
        comment: customReason,
        lang: selectedMessage?.lang || "en",
        thread_id: threadID,
        input_type: selectedMessage?.input_type || "text"
        
      }),
    });

    const data =
      await response.json();

    if (data.success) {
      setIsTyping(false)
      setMessages(prev => [
        ...prev,
        {
          text: data.improved_answer,
          isUser: false,
          animate: true,
          lang: selectedMessage.lang,
          improved: true,
          question: selectedMessage.question
        }
      ]);

      toast.success(
        "Improved answer generated"
      );
    }
    setIsTyping(false)
    setShowFeedbackModal(false);

  } catch (err) {
    setIsTyping(false)
    console.error(err);
  }
};


  const submitFeedback = async (
  msg,
  feedback
) => {
  try {

    if (msg.feedback) {
      toast.info(
        "Feedback already submitted"
      );
      return;
    }

    await fetch(
      `${BASE_URL}/feedback`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
      
      body: JSON.stringify({
      thread_id: threadID,
      question: msg.question || "",
      answer: msg.text,
      feedback,
      reason: feedback === "dislike" ? feedbackReason : null,
      comment: feedback === "dislike" ? customReason : null,
    })
      }
    );

    setMessages(prev =>
      prev.map(m =>
        m === msg
          ? { ...m, feedback }
          : m
      )
    );

    toast.success(
      "Feedback submitted"
    );

  } catch (err) {
    console.error(err);
  }
};
  

  const loadThreads = async (id) => {
    try {
      const response = await fetch(`${BASE_URL}/threads/thread/${id}`);

      const res = await response.json();

      if (res.success) {
        setThreads(res.threads);
      }
    } catch (error) {
      console.error(
        "Failed to load threads",
        error
      );
    }
};
  const loadThreadMessages = async (threadId) => {
    setloadPastChat(true)
    try {
      setSelectedThread(threadId);
      const response = await fetch(
        `${BASE_URL}/threads/${threadId}`
      );

      const res = await response.json();

      if (!res.success){
        setloadPastChat(false)
        return;
      }

      const state = res.state;

      const restoredMessages =
        (state.chat_history || []).map((msg) => ({
          text: msg.text,
          isUser: msg.role === "user",
          imagePreview: msg.image_url || null,
          animate:false,
          lang:msg.lang
        }));
        setTimeout(()=>{
            setloadPastChat(false)
        },2000)
        
        setMessages(restoredMessages);

      // continue conversation in same thread
      set_threadID(threadId);
      

    } catch (error) {
      console.error(error);
    }
};


  
  useEffect(() =>{
    const id=localStorage.getItem("user_id") || "user01"
    if (id){
      setuserId(id)

      loadThreads(id);
    }
    
    
  }, []);


  const sendTextToBackend = async (userMessage, input_t, image = null) => {
  setIsTyping(true);
  try {
    const data = {
      message: userMessage,
      thread_id: threadID || null,
      input_type: input_t,
      user_id: user_id,
      ...(image && {
        image_id: image.image_id,
        image_path: image.image_path,
        disease_prediction: image.best_prediction,
        image_url: image.image_url,
        disease_predictions: image.predictions || null,
      }),
    };

    const response = await fetch(`${BASE_URL}/chat/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.log("Status:", response.status);
      setIsTyping(false);
      if (response.status === 400) {
        const ans = "This language is not supported. Try some other!";
        setMessages((prev) => [...prev, { text: ans, isUser: false, animate: true, lang: "en", error: true }]);
        return;
      }
      setMessages((prev) => [...prev, { text: "Can't fetch answer right now. Try again!", isUser: false, animate: true, lang: "en", error: true }]);
      return;
    }

    const res = await response.json();
    console.log(res);
    if (res.success) {
      if (res.thread_id) {
        set_threadID(res.thread_id);
      }
      await loadThreads(user_id);

      if (res.interrupt) {
        const questions = res.data.questions ?? [res.data.question];
        setMessages(prev => [
          ...prev,
          ...questions.map(q => ({ text: q, isUser: false, animate: true, lang: q.user_lang, showSuggestions: false }))
        ]);
        setIsTyping(false);
        return;
      }

      setIsTyping(false);
      const fin = res.answer;
      const user_lang = res.user_lang;
      const s_ques = res.suggested_ques;

      setMessages((prev) => [...prev, {
        text: fin,
        isUser: false,
        animate: true,
        lang: user_lang,
        ques: s_ques || [],
        disease_prediction: res.disease_prediction || null,
      }]);

      if (input_t === "audio" && res.audio) {
        const audio = new Audio(`data:audio/wav;base64,${res.audio}`);
        audio.play();
      }
    } else {
      setIsTyping(false);
      if (res.error === "Translation failed") {
        toast.error("This Language is not supported, Try some other languages.");
        return;
      }
      toast.error("Can't fetch answer Try again!");
    }
  } catch (error) {
    setIsTyping(false);
    console.log(error);
    toast.error("Something went wrong");
  }
};

const handleSubmit = (e) => {
  e?.preventDefault();
  if (input.trim() === "" && !pendingImage) return;

  const userMessage = input;
  setMessages((prev) => [...prev, {
    text: userMessage || "(image)",
    isUser: true,
    imagePreview: pendingImage?.previewUrl || null,
    disease_prediction: pendingImage?.best_prediction || null,
  }]);

  const imageToSend = pendingImage;
  setInput("");
  clearPendingImage();

  sendTextToBackend(userMessage, "text", imageToSend);

};

const sendAudioToBackend = async (audioBlob) => {
  try {
    const formData = new FormData();
    formData.append("audio", audioBlob, `recording-${Date.now()}.webm`);

    const response = await fetch(`${BASE_URL}/audio/transcribe`, {
      method: "POST",
      body: formData,
    });

    const res = await response.json();
    const transcript = res.transcript.transcript;

    setMessages((prev) => [...prev, {
      text: transcript,
      isUser: true,
      imagePreview: pendingImage?.previewUrl || null,
      disease_prediction: pendingImage?.best_prediction || null,
    }]);

    const imageToSend = pendingImage;
    clearPendingImage();

    sendTextToBackend(transcript, "audio", imageToSend);
  } catch (error) {
    console.error(error);
  }
};

// image upload — unchanged from before
const [pendingImage, setPendingImage] = useState(null);
const imageInputRef = useRef(null);
const cameraInputRef = useRef(null);

const handleImageUpload = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    toast.error("Please upload an image file");
    return;
  }

  const previewUrl = URL.createObjectURL(file);
  setPendingImage({ uploading: true, previewUrl });

  try {
    const formData = new FormData();
    formData.append("image", file);
    const res = await fetch(`${BASE_URL}/image/predict`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    setPendingImage({
      uploading: false,
      previewUrl,
      image_id: data.image_id,
      image_path: data.image_path,
      image_url: data.image_url,
      best_prediction: data.best_prediction,
    });
  } catch (err) {
    console.error(err);
    toast.error("Image analysis failed");
    setPendingImage(null);
  }
  e.target.value = "";
};

const clearPendingImage = () => setPendingImage(null);
  
const handleDeleteThread = async (threadId) => {
  try {
    const res = await fetch(
      `${BASE_URL}/threads/${threadId}`,
      {
        method: "DELETE",
      }
    );

    const data = await res.json();

    if (data.success) {
      setThreads((prev) =>
        prev.filter((t) => t.thread_id !== threadId)
      );
      toast.success("Chat deleted Successfully")
      if (selectedThread === threadId) {
        setSelectedThread(null);
        setMessages([]);
        set_threadID(null);
      }
    }
  } catch (error) {
    console.error(error);
    toast.error("Chat could not be deleted. Try again!")
  }
};
  const [isRecording, setIsRecording] = useState(false);
  const RECORDING_DURATION = 10000; // 10 seconds
  const recordingTimeoutRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const intervalRef = useRef(null);
  
  const startRecording = async () => {
      setTimeLeft(RECORDING_DURATION / 1000);

      clearInterval(intervalRef.current);

      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(intervalRef.current);
            return 0;
          }
        
          return prev - 1;
        });
      }, 1000);

  try
    {
      const stream = await navigator.mediaDevices.getUserMedia(
      {
        audio: true,
      });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
    
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      mediaRecorder.onstop = async () => {
        clearInterval(intervalRef.current);
      
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
      
        await sendAudioToBackend(audioBlob);
      
        stream.getTracks().forEach((track) => track.stop());
      
        setTimeLeft(0);
        setIsRecording(false);
      };
    
      mediaRecorder.start();
      setIsRecording(true);
    
      recordingTimeoutRef.current = setTimeout(() => {
        if(mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") 
        {
          mediaRecorderRef.current.stop();
        }
      }, RECORDING_DURATION);

   }
   catch (error) 
   {
    console.error(error);
   }
};

const stopRecording = () => {
  if (
    mediaRecorderRef.current &&
    mediaRecorderRef.current.state === "recording"
  ) {
    clearTimeout(recordingTimeoutRef.current);
    clearInterval(intervalRef.current);

    mediaRecorderRef.current.stop();

    setTimeLeft(0);
    setIsRecording(false);
  }
};

const handleAudioUpload = async (e) => {
  const file = e.target.files[0];

  if (!file) return;

  if (!file.type.startsWith("audio/")) {
    toast.error("Please upload an audio file");
    return;
  }

  try {
    await sendAudioToBackend(file);
  } catch (error) {
    console.error(error);
    toast.error("Failed to upload audio");
  }

  // reset input so same file can be selected again
  e.target.value = "";
};

useEffect(() => {
  return () => {
    clearTimeout(recordingTimeoutRef.current);
    clearInterval(intervalRef.current);
  };
}, []);

  const clearChat = () => {
    setMessages([]);
    set_threadID(null);
    setSelectedThread(null);
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


  const speakText = async(text,lang) => {
    try 
    {
      console.log(text)
      console.log(lang)
    const response = await fetch(`${BASE_URL}/play/dictate_text`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_lang: lang,
        text: text,
      }),
    });

    const data = await response.json();
    console.log(data)
    if (data.success) {
      console.log("Audio received:", data.audio);
      const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
       setTimeout(() => {
    
    audio.play();
  }, 1000);

    } else {
      console.error("Error:", data.error);
    }

  } catch (error) {
    console.error("API call failed:", error);
  }

};

const handleShowSuggestions = (index) => {
  setMessages((prev) =>
    prev.map((m, i) =>
      i === index
        ? { ...m, showSuggestions: true }
        : m
    )
  );
};

const handleSuggestedClick = (question) => {
  
  const userMessage = question;
  setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);
  setInput("");
  // optional small delay so UI updates first
  setTimeout(() => {
    sendTextToBackend(question,"text"); 
  }, 100);
};



return (
  <>
  <div className="h-screen bg-[#F8F4E9] overflow-hidden">
  <Toaster richColors position="top-center" />

  <div className="flex h-full">
    {/* Sidebar CHAT HISTORY SECTION */}
    <div className="w-[30%] bg-[#F1EFE2] border-r border-[#D9CFB0] flex flex-col">

      {/* Header */}
      <div className="p-5 border-b border-[#D9CFB0]">
        <div className="flex items-center justify-between">
          <h2 className="text-[#3D2B1F] text-2xl font-semibold">
            Chat History
          </h2>
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={clearChat}
              className="
                flex items-center gap-2
                px-3 py-2
                rounded-lg
                bg-[#C17817]
                text-white
                hover:bg-[#A8650F]
                transition-all duration-200
                cursor-pointer
              "
            >
              <NotebookPen size={18} strokeWidth={2} />
              <span className="text-sm font-medium">
                New Chat
              </span>
            </button>
            <Component user_id={user_id} />
          </div>
        </div>
      </div>

      {/* PAST CHATS */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {threads.length === 0 ? (
          <p className="text-lg text-[#8A7A5C] flex items-center justify-center">
            No Past Chats
          </p>
        ) : (
          threads.map((thread) => (
            <div
              key={thread.thread_id}
              onClick={() => loadThreadMessages(thread.thread_id)}
              className={`
                rounded-lg p-3 cursor-pointer transition
                ${
                  selectedThread === thread.thread_id
                    ? "bg-[#4C7A3D] text-white"
                    : "bg-[#EDE7D2] hover:bg-[#E3DABF] text-[#3D2B1F]"
                }
              `}
            >
              <div className="text-md font-medium truncate">
                {thread.title}
              </div>
              <div className="flex justify-between items-center mt-1">
                <div className="text-xs text-[#8A7A5C]">
                  {thread.created_at}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteThread(thread.thread_id);
                  }}
                  className="text-[#8A7A5C] hover:text-[#B3441E] ml-2 cursor-pointer"
                >
                  <Trash size={20} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>

   

    <div className="w-[70%] flex flex-col h-full bg-[#F8F4E9]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
          {loadPastChat ? (
              <ChatSkeleton />
            ) :messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Sparkles className="h-14 w-14 text-[#C17817] mx-auto mb-4" />

                <h3 className="text-[#3D2B1F] text-2xl font-semibold mb-2">
                  How can I assist you today?
                </h3>

                <p className="text-[#6B5A3E]">
                  Let’s resolve your queries and find the best schemes for you
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-[90%] mx-auto space-y-6 ">
              {messages.map((msg, index) => (
                <div
              key={index}
              className={`flex ${
                msg.isUser ? "justify-end" : "justify-start"
              }`}>
                <div className="group max-w-[75%]">

                  {msg.imagePreview && (
                  
                    <Image
                      src={msg.imagePreview}
                      alt="Uploaded crop image preview"
                      width={160}   // matches w-40
                      height={160}  // matches h-40
                      className="w-40 h-40 object-cover rounded-xl mb-2 ml-auto"
                    />
                  )}
                  {msg.disease_prediction && (
                    <div className="text-xs text-[#8A7A5C] mb-1 ml-auto text-right">
                      Detected: {msg.disease_prediction.crop} – {msg.disease_prediction.disease}
                      {" "}({Math.round(msg.disease_prediction.confidence * 100)}%)
                    </div>
                  )}
    
                <div
                  className={`
                    px-4
                    py-3
                    rounded-2xl
                    animate-fade-in
                    ${
                      msg.isUser
                        ? "bg-[#5B4632] text-white"
                        : msg.error
                        ? "bg-[#FBEAEA] text-[#8A2E1F] border border-[#E3B8AE]"
                        : "bg-white text-[#3D2B1F] border border-[#E3DABF]"
                    }
                  `}
                >
              <div
                className={`
                  text-md
                  leading-[1.6]
                  tracking-[0.2px]
                  [&_h1]:text-2xl
                  [&_h1]:font-bold
                  [&_h2]:text-xl
                  [&_h2]:font-semibold
                  [&_ul]:list-disc
                  [&_ul]:pl-5
                  [&_ol]:list-decimal
                  [&_ol]:pl-5
                  [&_li]:my-1
                  [&_p]:mb-2
                  [&_strong]:font-bold
                  ${!msg.user && msg.error ?
                    " text-[#8A2E1F] font-semibold": ""
                  }
                  `}
              >
                {msg.isUser ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.text}
                </ReactMarkdown>
              ) : msg.animate ? (
                /* 🤖 AI MESSAGE → typing effect */
               <div>
              <TextType
                text={msg.text}
                typingSpeed={30}
                showCursor={true}
                cursorCharacter="|"
                onComplete={() => handleShowSuggestions(index)}
                variableSpeed={{ min: 10, max: 25 }}
                render={(text) => (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}
                    components={{
                        p: ({ children }) => <span>{children}</span>,
                      }}>
                    {text}
                  </ReactMarkdown>
                )}
              />

    {!msg.isUser &&
  msg.showSuggestions &&
  Array.isArray(msg.ques) &&
  msg.ques.filter(q => q?.trim()).length > 0 && (
      <div className="mt-3">
        <div className="text-lg text-[#8A7A5C] mb-2">
          Suggestion:
        </div>

        <div className="flex flex-col gap-2">
          {msg.ques.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSuggestedClick(q)}
              className="
                text-left
                text-[#3B7A9E]
                underline
                decoration-1
                hover:text-[#2E6580]
                transition
                flex items-start gap-2
                cursor-pointer
              "
            >
              <span>-</span>
              <span>{q}</span>
            </button>
          ))}
        </div>
      </div>
    )}
  </div>

        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {msg.text}
          </ReactMarkdown>
        )}
              </div>
            </div>
              {/* Feedback Buttons */}
                {!msg.isUser  && !msg.error && (
                    <div
                      className="
                        flex
                        items-center
                        gap-1
                        mt-1
                        ml-1
                        transition-opacity
                        duration-200
                      "
                    >

                      <button
                        onClick={() =>
                          submitFeedback(msg, "like")
                        }
                        className="
                          p-1.5
                          rounded-md
                          text-[#8A7A5C]
                          hover:text-[#4C7A3D]
                          hover:bg-[#EDE7D2]
                          cursor-pointer
                        "
                      >
                        <ThumbsUp
                              size={14}
                              className={
                                msg.feedback === "like"
                                    ? "bg-[#4C7A3D]/15 text-[#4C7A3D]"
                                    : "text-[#8A7A5C] hover:text-[#4C7A3D] hover:bg-[#EDE7D2]"
                              }
                            />
                      </button>

                      <button
                        onClick={() => {
                          setSelectedMessage(msg);
                          setFeedbackReason("");
                          setCustomReason("");
                          setShowFeedbackModal(true);
                        }}
                        className="
                          p-1.5
                          rounded-md
                          text-[#8A7A5C]
                          hover:text-[#B3441E]
                          hover:bg-[#EDE7D2]
                          cursor-pointer
                        "
                      >
                        <ThumbsDown
                          size={14}
                          className={
                               msg.feedback === "dislike"
                                  ? "bg-[#B3441E]/15 text-[#B3441E]"
                                  : "text-[#8A7A5C] hover:text-[#B3441E] hover:bg-[#EDE7D2]"
                          }
                        />
                      </button>
                      <button
                          onClick={() => speakText(msg.text,msg.lang)}
                          className="
                          p-1.5
                          rounded-md
                          text-[#8A7A5C]
                          hover:bg-[#EDE7D2]
                          cursor-pointer
                        "
                          title="Speak"
                        >
                          <Volume2
                          size={18}/>
                        </button>
                    </div>
                    )}

                  </div>
                </div>
                      ))}

                      {isTyping && (
                        <div className="flex justify-start">
                          <div className="bg-white border border-[#E3DABF] rounded-2xl px-4 py-3">
                            <div className="flex gap-2">
                              <div className="w-2 h-2 rounded-full bg-[#C17817] animate-bounce animation-duration:[0.5s]" />
                              <div className="w-2 h-2 rounded-full bg-[#C17817] animate-bounce delay-100 animation-duration:[0.5s]" />
                              <div className="w-2 h-2 rounded-full bg-[#C17817] animate-bounce delay-200 animation-duration:[0.5s]" />
                            </div>
                          </div>
                        </div>
                      )}

                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </div>
                
              {/* {CHAT BAR MODULE} */}

        <div
          className="bg-[#F1EFE2] p-4 "
        >
          {pendingImage && (
          <div className="flex items-center gap-2 mb-2 px-3 py-2 bg-white rounded-xl border border-[#D9CFB0] max-w-3xl mx-auto">
            {/* <img src={pendingImage.previewUrl} className="h-10 w-10 rounded object-cover" /> */}
            <Image
              src={pendingImage.previewUrl}
              alt="Uploaded crop image"
              width={40}
              height={40}
              className="h-10 w-10 rounded object-cover"
            />
            {pendingImage.uploading ? (
              <span className="text-sm text-[#6B5A3E]">Analyzing image…</span>
            ) : (
              <span className="text-sm text-[#6B5A3E]">
                {pendingImage.best_prediction?.crop} – {pendingImage.best_prediction?.disease}
              </span>
            )}
            <button type="button" onClick={clearPendingImage} className="ml-auto text-[#6B5A3E]">✕</button>
          </div>
        )}
          <form
            onSubmit={handleSubmit}
            className="max-w-3xl mx-auto"
          >
            <div className="relative">
              <input
                type="file"
                ref={fileInputRef}
                accept="audio/*"
                onChange={handleAudioUpload}
                className="hidden"
              />
              <input type="file" ref={imageInputRef} accept="image/*" onChange={handleImageUpload} className="hidden" />
              <input type="file" ref={cameraInputRef} accept="image/*" capture="environment" onChange={handleImageUpload} className="hidden" />
              
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Message AI Assistant..."
                className="
                  w-full
                  bg-white
                  border
                  border-[#D9CFB0]
                  rounded-3xl
                  py-4
                  pl-5
                  pr-14
                  text-[#3D2B1F]
                  placeholder:text-[#A8967A]
                  focus:outline-none
                  focus:ring-2
                  focus:ring-[#C17817]
                "
                onInput={(e) => {
                  e.currentTarget.style.height = "auto";
                  e.currentTarget.style.height = e.currentTarget.scrollHeight + "px";
                }}
              />
              
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => fileInputRef.current.click()}
                  className="
                    p-2
                    rounded-full
                    bg-[#EDE7D2]
                    text-[#6B5A3E]
                    hover:bg-[#E3DABF]
                    cursor-pointer
                  "
                >
                  <Paperclip className="h-5 w-5" />
                </button>
                <button
                  type="button"
                  onClick={() => imageInputRef.current.click()}
                  className="p-2 rounded-full bg-[#EDE7D2] text-[#6B5A3E] hover:bg-[#E3DABF] cursor-pointer"
                >
                  <ImageIcon className="h-5 w-5" />
                </button>
                <button
                  type="button"
                  onClick={() => cameraInputRef.current.click()}
                  className="p-2 rounded-full bg-[#EDE7D2] text-[#6B5A3E] hover:bg-[#E3DABF] cursor-pointer"
                >
                  <Camera className="h-5 w-5" />
                </button>
                <button
                  type="button"
                  onClick={
                    isRecording
                      ? stopRecording
                      : startRecording
                  }
                  className={`
                    p-2
                    rounded-full
                    transition-colors
                    ${
                      isRecording
                        ? "bg-red-600 text-white"
                        : "bg-[#EDE7D2] text-[#6B5A3E] hover:bg-[#E3DABF]"
                    }
                  `}
                >
                  <div className="flex gap-1.5">
                  {isRecording ? (
                    <Square className="h-5 w-5" />
                  ) : (
                    <Mic className="h-5 w-5 cursor-pointer"  />
                  )}
                  {isRecording && (
                    <span className="text-white-400 text-md">
                      {timeLeft}s
                    </span>
                  )}
                  </div>
                </button>
                
                <button
                  type="submit"
                  // disabled={!input.trim()}
                  disabled={(!input.trim() && !pendingImage) || pendingImage?.uploading}
                  className={`
                    p-2
                    rounded-full
                    ${
                      // !input.trim()
                      (!input.trim() && !pendingImage) || pendingImage?.uploading
                        ? "bg-[#EDE7D2] text-[#B0A47F]"
                        : "bg-[#4C7A3D] text-white hover:bg-[#3F6633] cursor-pointer"
                    }
                  `}
                >
                  {isTyping ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </button>
                
              </div>
            </div>
          </form>
        </div>
</div>
        {/* Input Section */}
        

        <style>
          {`
          @keyframes fade-in {
            from {
              opacity: 0;
              transform: translateY(8px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          .animate-fade-in {
            animation: fade-in 0.3s ease-out forwards;
          }

          .delay-75 {
            animation-delay: 0.2s;
          }

          .delay-150 {
            animation-delay: 0.4s;
          }
        `}
        </style>
      </div>
    </div>
    {
showFeedbackModal && (
<div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">

  <div className="bg-white border border-[#D9CFB0] p-6 rounded-2xl w-[500px] shadow-2xl">

    <h3 className="text-[#3D2B1F] text-xl font-medium mb-5">
      What didn't you like?
    </h3>

    <div className="space-y-3">

      {reasons.map(reason => (
        <button
          key={reason}
          onClick={() => setFeedbackReason(reason)}
          className={`
            w-full text-left p-3.5 rounded-xl
            text-sm text-[#3D2B1F]
            transition-all duration-200
            border
            ${
              feedbackReason === reason
                ? "bg-[#C17817]/10 border-[#C17817] text-[#3D2B1F] ring-1 ring-[#C17817]"
                : "bg-[#F1EFE2] border-[#D9CFB0] hover:bg-[#E3DABF] hover:border-[#C9BB92]"
            }
          `}
        >
          {reason}
        </button>
      ))}

    </div>

    {
      feedbackReason === "Other" && (
        <textarea
          value={customReason}
          onChange={(e) => setCustomReason(e.target.value)}
          className="
            mt-4
            w-full
            p-3.5
            rounded-xl
            bg-[#F8F4E9]
            border border-[#D9CFB0]
            text-[#3D2B1F]
            placeholder:text-[#A8967A]
            focus:outline-none
            focus:ring-1
            focus:ring-[#C17817]
            resize-none
          "
          rows={4}
          placeholder="Tell us more..."
        />
      )
    }

    <div className="flex justify-end gap-3 mt-6">

      <button
        onClick={() => setShowFeedbackModal(false)}
        className="
          px-4 py-2.5
          rounded-xl
          text-[#6B5A3E]
          bg-[#F1EFE2]
          border border-[#D9CFB0]
          hover:bg-[#E3DABF]
          transition
          cursor-pointer
        "
      >
        Cancel
      </button>

      <button
        onClick={regenerateAnswer}
        disabled={!feedbackReason}
        className="
          px-4 py-2.5
          rounded-xl
          bg-[#4C7A3D]
          text-white
          hover:bg-[#3F6633]
          disabled:opacity-50
          disabled:cursor-not-allowed
          transition
          cursor-pointer
        "
      >
        Regenerate
      </button>
    </div>
  </div>
</div>
  )
  }
  </>
);
};

export default AIMessageBar;