import React, {useState} from 'react';
import { useNavigate, useParams}

export const Loading: React.FC = () => {
  const [results, setResults] = useState(['']) 
  return (
    <>
      
      <h1>Hang tight- your resume is being analyzed...</h1>

    </>
  )
}


export default Loading;