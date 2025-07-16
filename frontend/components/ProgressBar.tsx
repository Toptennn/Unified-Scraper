import React from 'react';

interface ProgressBarProps {
  progress: number;
  label?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress, label }) => {
  const clamped = Math.min(100, Math.max(0, progress));
  return (
    <div className="w-full">
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
        <div
          className="bg-blue-600 dark:bg-blue-500 h-4 transition-all"
          style={{ width: `${clamped}%` }}
        ></div>
      </div>
      {label && (
        <p className="text-sm text-center text-gray-700 dark:text-gray-300 mt-1">
          {label}
        </p>
      )}
    </div>
  );
};

export default ProgressBar;
