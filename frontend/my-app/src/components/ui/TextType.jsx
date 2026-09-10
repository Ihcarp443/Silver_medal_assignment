'use client';

import {
  useEffect,
  useRef,
  useState,
  createElement,
  useMemo,
  useCallback
} from 'react';
import { gsap } from 'gsap';

const TextType = ({
  text,
  as: Component = 'div',
  render,
  typingSpeed = 50,
  initialDelay = 0,
  className = '',
  showCursor = true,
  cursorCharacter = '|',
  cursorClassName = '',
  cursorBlinkDuration = 0.5,
  textColors = [],
  variableSpeed,
  onComplete, // ✅ new callback
  startOnVisible = false,
  reverseMode = false,
  ...props
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentCharIndex, setCurrentCharIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(!startOnVisible);
  const [isDone, setIsDone] = useState(false); // ✅ track completion

  const cursorRef = useRef(null);
  const containerRef = useRef(null);

  const textArray = useMemo(() => {
    if (!text) return [''];
    return Array.isArray(text) ? text : [text];
  }, [text]);

  const getRandomSpeed = useCallback(() => {
    if (!variableSpeed) return typingSpeed;
    const { min = 20, max = 60 } = variableSpeed;
    return Math.random() * (max - min) + min;
  }, [variableSpeed, typingSpeed]);

  const getCurrentTextColor = () => {
    if (textColors.length === 0) return 'inherit';
    return textColors[0];
  };

  // visibility observer
  useEffect(() => {
    if (!startOnVisible || !containerRef.current) return;

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) setIsVisible(true);
      });
    });

    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [startOnVisible]);
  
  useEffect(() => {
  setDisplayedText("");
  setCurrentCharIndex(0);
  setIsDone(false);
}, [text]);

  // cursor blink (only while typing)
  useEffect(() => {
    if (!showCursor || !cursorRef.current) return;

    gsap.set(cursorRef.current, { opacity: 1 });

    gsap.to(cursorRef.current, {
      opacity: 0,
      duration: cursorBlinkDuration,
      repeat: -1,
      yoyo: true,
      ease: 'power2.inOut'
    });
  }, [showCursor, cursorBlinkDuration]);

  // typing logic (NO DELETE ANYMORE)
  useEffect(() => {
    if (!isVisible || isDone) return;

    let timeout;

    const fullText = textArray[0] || '';
    const processedText = reverseMode
      ? fullText.split('').reverse().join('')
      : fullText;

    const type = () => {
      if (currentCharIndex < processedText.length) {
        timeout = setTimeout(() => {
          setDisplayedText(prev => prev + processedText[currentCharIndex]);
          setCurrentCharIndex(prev => prev + 1);
        }, variableSpeed ? getRandomSpeed() : typingSpeed);
      } else {
        setIsDone(true);
        onComplete?.();
      }
    };

    if (currentCharIndex === 0 && displayedText === '') {
      timeout = setTimeout(type, initialDelay);
    } else {
      type();
    }

    return () => clearTimeout(timeout);
  }, [
    getRandomSpeed,
    currentCharIndex,
    displayedText,
    typingSpeed,
    initialDelay,
    textArray,
    isVisible,
    isDone,
    reverseMode,
    variableSpeed,
    onComplete
  ]);

  // cursor should disappear after completion
  const shouldShowCursor = showCursor && !isDone;

  return createElement(
    Component,
    {
      ref: containerRef,
      className: `whitespace-pre-wrap tracking-tight ${className}`,
      ...props
    },
    <>
        <span
        className="inline"
        style={{ color: getCurrentTextColor() }}
        >
          {render ? render(displayedText) : displayedText}
        </span>
      {shouldShowCursor && (
        <span
          ref={cursorRef}
          className={`ml-1 inline-block ${cursorClassName}`}
        >
          {cursorCharacter}
        </span>
      )}
    </>
  );
};

export default TextType;

