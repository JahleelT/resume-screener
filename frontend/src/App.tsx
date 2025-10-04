import { useState } from 'react'
import { Routes, Route } from "react-router-dom"

import Home from "./pages/Home";
import History from "./pages/History";
import Loading from "./pages/Loading";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import Result from "./pages/Result";

import './css'

function App() {
  

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/history" element={<History />} />
      <Route path="/loading" element={<Loading />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/result" element={<Result />} />
    </Routes>
  )
}

export default App
