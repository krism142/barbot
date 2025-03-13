import React, { createContext, useState, useContext, useEffect } from "react"
import axios from "axios"

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem("token"))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setLoading(false)
        return
      }

      try {
        const response = await axios.get("/api/users/me", {
          headers: { Authorization: "Bearer " + token }
        })
        setUser(response.data)
      } catch (err) {
        console.error("Authentication error:", err)
        setError(err.response?.data?.detail  "Failed to authenticate")
        logout()
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [token])

  const login = async (username, password) => {
    try {
      setLoading(true)
      setError(null)
      
      // Create form data for token endpoint
      const formData = new FormData()
      formData.append("username", username)
      formData.append("password", password)

      const response = await axios.post("/api/token", formData)
      const { access_token } = response.data
      
      // Save token and fetch user
      localStorage.setItem("token", access_token)
      setToken(access_token)
      return true
    } catch (err) {
      console.error("Login error:", err)
      setError(err.response?.data?.detail  "Login failed")
      return false
    } finally {
      setLoading(false)
    }
  }

  const register = async (userData) => {
    try {
      setLoading(true)
      setError(null)
      
      await axios.post("/api/register", userData)
      return true
    } catch (err) {
      console.error("Registration error:", err)
      setError(err.response?.data?.detail  "Registration failed")
      return false
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem("token")
    setToken(null)
    setUser(null)
  }

  // Create axios interceptor for adding auth headers
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        if (token) {
          config.headers.Authorization = "Bearer " + token
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    return () => {
      axios.interceptors.request.eject(interceptor)
    }
  }, [token])

  const value = {
    user,
    token,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!token  !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
