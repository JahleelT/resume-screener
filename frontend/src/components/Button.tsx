import React from 'react';
import "tailwindcss"; 

interface ButtonProps {
  children: React.ReactNode;
  color?: string;
  textColor ?: string;
  onClick ?: (() => void);
}


export const Button: React.FC<ButtonProps> = ({ children, color="bg-blue-500", textColor="text-black", onClick}) => {

  return (
    <button
    onClick={onClick}
    className={`px-4 py-2 ${color} border border-black ${textColor}, font-semibold rounded-lg shadow-md transition mt-2 w-full`}>
      {children}
    </button>
  );
}

export default Button;