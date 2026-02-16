import React, { useState, useRef, useEffect } from 'react';
import { Sun, Moon, Monitor, ChevronDown } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const themeOptions = [
    { id: 'light', icon: Sun, label: 'Light' },
    { id: 'dark', icon: Moon, label: 'Dark' },
    { id: 'system', icon: Monitor, label: 'System' },
  ] as const;

  const currentOption = themeOptions.find(opt => opt.id === theme) || themeOptions[2];
  const Icon = currentOption.icon;

  return (
    <div
      ref={containerRef}
      className="relative flex flex-col items-center"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      {/* Main Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`z-50 p-2.5 rounded-full transition-all duration-300 border shadow-lg backdrop-blur-md flex items-center justify-center
          ${isOpen ? 'bg-[var(--docu-sidebar)] border-[var(--docu-accent)]/50 scale-110' : 'bg-[var(--docu-sidebar)]/80 border-[var(--docu-border)] hover:border-[var(--docu-accent)]/30'}
        `}
        title={`Theme: ${currentOption.label}`}
      >
        <Icon className={`w-5 h-5 transition-colors ${isOpen ? 'text-[var(--docu-accent)]' : 'text-[var(--docu-text-main)]'}`} />
      </button>

      {/* Vertical Dropdown */}
      <div
        className={`absolute top-full mt-2 flex flex-col gap-2 transition-all duration-300 transform origin-top
          ${isOpen ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 -translate-y-4 pointer-events-none'}
        `}
      >
        {themeOptions.map((option) => {
          const OptionIcon = option.icon;
          const isActive = theme === option.id;

          return (
            <button
              key={option.id}
              onClick={() => {
                setTheme(option.id);
                setIsOpen(false);
              }}
              className={`p-2.5 rounded-full transition-all duration-200 border shadow-md backdrop-blur-sm flex items-center justify-center group
                ${isActive
                  ? 'bg-white dark:bg-[var(--docu-bg)] border-[var(--docu-accent)] text-[var(--docu-accent)]'
                  : 'bg-[var(--docu-sidebar)]/90 border-[var(--docu-border)] text-[var(--docu-text-secondary)] hover:text-[var(--docu-text-main)] hover:border-[var(--docu-accent)]/30 hover:scale-105'}
              `}
              title={option.label}
            >
              <OptionIcon className="w-5 h-5" />
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ThemeToggle;
