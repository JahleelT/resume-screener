import { useState, useEffect } from 'react';

export function useJobStatus(jobId) {
  const [status, setStatus] = useState("pending");
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    let isMounted = true;
    let timeoutId;

    const checkStatus = async () => {
      try {
        const res = await fetch(`/api/status/${jobId}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        setStatus(data.status);

        if (data.status === "pending") {
          timeoutId = setTimeout(checkStatus, 2000);
        } 
      } catch (err) {
        console.error("Error checking job status:", err);
        setError(err);

        if (isMounted) timeoutId = setTimeout(checkStatus, 2000);
      }
    }

    checkStatus();

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, [jobId]);

  return { status, error };
}