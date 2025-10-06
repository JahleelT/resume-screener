import React from 'react';
import "tailwindcss"; 

interface ButtonProps {
  childrem: React.ReactNode;
  color?: string;
  textColor ?: string;
  onClick ?: (() => void);
  disabled ?: boolean;
}


export const Button: React.FC<ButtonProps> = ( children) => {

  return (
    <button></button>
  )
}

export default Button;