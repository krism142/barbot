import React, { useState } from "react"
import LoginForm from "./LoginForm"
import RegisterForm from "./RegisterForm"

const AuthPage = ({ onAuthSuccess }) => {
  const [activeTab, setActiveTab] = useState("login")

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-center text-indigo-600">Barbot</h1>
            <p className="text-center text-gray-600 mt-2">
              Your virtual mixologist with 20+ years of experience
            </p>
          </div>

          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="flex border-b">
              <button
                onClick={() => setActiveTab("login")}
                className={w-1/2 py-3 px-4 font-medium text-center {
                  activeTab === "login"
                    ? "bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600"
                    : "text-gray-600 hover:bg-gray-50"
                }}
              >
                Sign In
              </button>
              <button
                onClick={() => setActiveTab("register")}
                className={w-1/2 py-3 px-4 font-medium text-center {
                  activeTab === "register"
                    ? "bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600"
                    : "text-gray-600 hover:bg-gray-50"
                }}
              >
                Register
              </button>
            </div>

            <div className="p-6">
              {activeTab === "login" ? (
                <LoginForm onSuccess={onAuthSuccess} />
              ) : (
                <RegisterForm onSuccess={() => setActiveTab("login")} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthPage
