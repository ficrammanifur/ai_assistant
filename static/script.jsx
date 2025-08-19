class AIAssistant {
  constructor() {
    this.isRecording = false
    this.recognition = null
    this.voiceEnabled = true

    this.initializeElements()
    this.initializeVoiceRecognition()
    this.initializeEventListeners()
    this.checkSystemStatus()
    this.setInitialTime()
  }

  initializeElements() {
    this.messageInput = document.getElementById("message-input")
    this.sendButton = document.getElementById("send-button")
    this.micButton = document.getElementById("mic-button")
    this.chatMessages = document.getElementById("chat-messages")
    this.voiceStatus = document.getElementById("voice-status")
    this.statusDot = document.getElementById("status-dot")
    this.statusText = document.getElementById("status-text")
    this.loading = document.getElementById("loading")

    // Control buttons
    this.clearChatButton = document.getElementById("clear-chat")
    this.toggleVoiceButton = document.getElementById("toggle-voice")
    this.systemStatusButton = document.getElementById("system-status")
  }

  initializeVoiceRecognition() {
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      this.recognition = new SpeechRecognition()

      this.recognition.continuous = false
      this.recognition.interimResults = false
      this.recognition.lang = "en-US"

      this.recognition.onstart = () => {
        this.isRecording = true
        this.micButton.classList.add("recording")
        this.voiceStatus.textContent = "Listening... Speak now!"
      }

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        this.messageInput.value = transcript
        this.voiceStatus.textContent = `Heard: "${transcript}"`
        setTimeout(() => this.sendMessage(), 500)
      }

      this.recognition.onerror = (event) => {
        this.voiceStatus.textContent = `Voice recognition error: ${event.error}`
        this.stopRecording()
      }

      this.recognition.onend = () => {
        this.stopRecording()
      }
    } else {
      this.voiceStatus.textContent = "Voice recognition not supported in this browser"
      this.micButton.style.display = "none"
    }
  }

  initializeEventListeners() {
    // Send message events
    this.sendButton.addEventListener("click", () => this.sendMessage())
    this.messageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.sendMessage()
      }
    })

    // Voice recording
    this.micButton.addEventListener("click", () => this.toggleRecording())

    // Control buttons
    this.clearChatButton.addEventListener("click", () => this.clearChat())
    this.toggleVoiceButton.addEventListener("click", () => this.toggleVoice())
    this.systemStatusButton.addEventListener("click", () => this.showSystemStatus())

    // Auto-resize input
    this.messageInput.addEventListener("input", () => {
      this.sendButton.disabled = !this.messageInput.value.trim()
    })
  }

  setInitialTime() {
    const initialTime = document.getElementById("initial-time")
    if (initialTime) {
      initialTime.textContent = new Date().toLocaleTimeString()
    }
  }

  async checkSystemStatus() {
    try {
      const response = await fetch("/status")
      const status = await response.json()

      if (status.ai_model_loaded) {
        this.statusDot.classList.add("connected")
        this.statusText.textContent = "AI Model Ready"
      } else {
        this.statusDot.classList.add("error")
        this.statusText.textContent = "AI Model Loading..."
      }
    } catch (error) {
      this.statusDot.classList.add("error")
      this.statusText.textContent = "Connection Error"
    }
  }

  toggleRecording() {
    if (!this.recognition || !this.voiceEnabled) {
      this.voiceStatus.textContent = "Voice recognition not available"
      return
    }

    if (this.isRecording) {
      this.recognition.stop()
    } else {
      this.recognition.start()
    }
  }

  stopRecording() {
    this.isRecording = false
    this.micButton.classList.remove("recording")
    if (!this.voiceStatus.textContent.includes("Heard:")) {
      this.voiceStatus.textContent = ""
    }
  }

  async sendMessage() {
    const message = this.messageInput.value.trim()
    if (!message) return

    // Add user message to chat
    this.addMessage(message, "user")
    this.messageInput.value = ""
    this.sendButton.disabled = true

    // Show loading
    this.showLoading(true)

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Add AI response to chat
      this.addMessage(data.response, "assistant")
    } catch (error) {
      console.error("Error:", error)
      this.addMessage("Sorry, I encountered an error. Please try again.", "assistant")
    } finally {
      this.showLoading(false)
      this.sendButton.disabled = false
    }
  }

  addMessage(content, sender) {
    const messageDiv = document.createElement("div")
    messageDiv.className = `message ${sender}-message`

    const contentDiv = document.createElement("div")
    contentDiv.className = "message-content"

    if (sender === "user") {
      contentDiv.innerHTML = `<strong>You:</strong> ${content}`
    } else {
      contentDiv.innerHTML = `<strong>AI Assistant:</strong> ${content}`
    }

    const timeDiv = document.createElement("div")
    timeDiv.className = "message-time"
    timeDiv.textContent = new Date().toLocaleTimeString()

    messageDiv.appendChild(contentDiv)
    messageDiv.appendChild(timeDiv)

    this.chatMessages.appendChild(messageDiv)
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight
  }

  showLoading(show) {
    if (show) {
      this.loading.classList.remove("hidden")
    } else {
      this.loading.classList.add("hidden")
    }
  }

  clearChat() {
    // Keep only the initial message
    const messages = this.chatMessages.querySelectorAll(".message")
    for (let i = 1; i < messages.length; i++) {
      messages[i].remove()
    }
  }

  toggleVoice() {
    this.voiceEnabled = !this.voiceEnabled
    this.toggleVoiceButton.textContent = this.voiceEnabled ? "Disable Voice" : "Enable Voice"
    this.micButton.style.opacity = this.voiceEnabled ? "1" : "0.5"

    if (!this.voiceEnabled && this.isRecording) {
      this.recognition.stop()
    }
  }

  async showSystemStatus() {
    try {
      const response = await fetch("/status")
      const status = await response.json()

      const statusMessage = `
System Status:
• AI Model: ${status.ai_model_loaded ? "Loaded ✓" : "Not Loaded ✗"}
• OLED Display: ${status.oled_available ? "Available ✓" : "Not Available ✗"}
• Chat History: ${status.chat_history_count} messages
• Voice Recognition: ${this.recognition ? "Available ✓" : "Not Available ✗"}
            `.trim()

      this.addMessage(statusMessage, "assistant")
    } catch (error) {
      this.addMessage("Unable to fetch system status.", "assistant")
    }
  }
}

// Initialize the AI Assistant when the page loads
document.addEventListener("DOMContentLoaded", () => {
  new AIAssistant()
})
