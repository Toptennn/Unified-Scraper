import React from 'react';

interface ProgressBarProps {
  progress: number;
  label?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress, label }) => {
  const clamped = Math.min(100, Math.max(0, progress));
  
  return (
    <div className="w-full space-y-2">
      <div className="relative w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden shadow-inner">
        <div
          className="h-full bg-gradient-to-r from-purple-500 to-purple-600 dark:from-purple-400 dark:to-purple-500 transition-all duration-300 ease-out rounded-full shadow-sm"
          style={{ width: `${clamped}%` }}
        >
          <div className="absolute inset-0 bg-white/20 rounded-full animate-pulse opacity-75"></div>
        </div>
        {/* Subtle shine effect */}
        <div 
          className="absolute top-0 left-0 h-full w-full bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12 transition-transform duration-1000"
          style={{ 
            transform: `translateX(${clamped * 4 - 100}%) skewX(-12deg)`,
            width: '50%'
          }}
        ></div>
      </div>
      {label && (
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600 dark:text-gray-400 font-medium">
            {label}
          </span>
          <span className="text-purple-600 dark:text-purple-400 font-semibold">
            100%
          </span>
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
