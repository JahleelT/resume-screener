import React, {useState, } from 'react';

export const Login: React.FC = () => {
  const [msg, setMsg] = useState("");
  return (
    <>
      <h1>Log In</h1>
      <ul className="list-none p-0 mb-4">
        <li className="p-2 rounded-b mb-2 font-medium">
          { msg }
        </li>
      </ul>
    </>
  )
}


export default Login;