import React, {useState} from 'react';
import "tailwindcss";

export const SignUp: React.FC = () => {
  const [msg, setMsg] = useState("");

  return (
    <>
    <h1>Sign In</h1>
    <ul className='list-none p-0 mb-4'>
      <li className='p-2 rounded-b mb-2 font-medium'>
        { msg }
      </li>
    </ul>
    </>
  )
}


export default SignUp;