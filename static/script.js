class AIAssistant {
  constructor() {
    this.chatMessages = document.getElementById("chat-messages")
    this.messageInput = document.getElementById("message-input")
    this.sendButton = document.getElementById("send-button")
    this.voiceButton = document.getElementById("voice-button")
    this.statusDiv = document.getElementById("status")

    this.isRecording = false
    this.recognition = null

    this.initializeEventListeners()
    this.initializeVoiceRecognition()
    this.updateStatus("Ready")
  }

  initializeEventListeners() {
    this.messageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        this.sendMessage()
      }
    })

    this.sendButton.addEventListener("click", () => this.sendMessage())
    this.voiceButton.addEventListener("click", () => this.toggleVoiceRecording())
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
        this.voiceButton.textContent = "🔴 Recording..."
        this.voiceButton.classList.add("recording")
        this.updateStatus("Listening...")
      }

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        this.messageInput.value = transcript
        this.updateStatus("Voice input received")
      }

      this.recognition.onend = () => {
        this.isRecording = false
        this.voiceButton.textContent = "🎤 Voice"
        this.voiceButton.classList.remove("recording")
        this.updateStatus("Ready")
      }

      this.recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error)
        this.isRecording = false
        this.voiceButton.textContent = "🎤 Voice"
        this.voiceButton.classList.remove("recording")
        this.updateStatus("Voice recognition error")
      }
    } else {
      this.voiceButton.disabled = true
      this.voiceButton.textContent = "🎤 Not Supported"
      console.warn("Speech recognition not supported in this browser")
    }
  }

  toggleVoiceRecording() {
    if (!this.recognition) return

    if (this.isRecording) {
      this.recognition.stop()
    } else {
      this.recognition.start()
    }
  }

  async sendMessage() {
    const message = this.messageInput.value.trim()
    if (!message) return

    this.addMessage("user", message)
    this.messageInput.value = ""
    this.updateStatus("AI is thinking...")

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

      if (data.error) {
        this.addMessage("assistant", `Error: ${data.error}`)
      } else {
        this.addMessage("assistant", data.response)
      }

      this.updateStatus("Ready")
    } catch (error) {
      console.error("Error sending message:", error)
      this.addMessage("assistant", "Sorry, I encountered an error. Please try again.")
      this.updateStatus("Error occurred")
    }
  }

  addMessage(sender, message) {
    const messageDiv = document.createElement("div")
    messageDiv.className = `message ${sender}-message`

    const avatar = document.createElement("div")
    avatar.className = "avatar"
    avatar.textContent = sender === "user" ? "👤" : "🤖"

    const content = document.createElement("div")
    content.className = "message-content"
    content.textContent = message

    messageDiv.appendChild(avatar)
    messageDiv.appendChild(content)

    this.chatMessages.appendChild(messageDiv)

    this.chatMessages.scrollTop = this.chatMessages.scrollHeight
  }

  updateStatus(status) {
    if (this.statusDiv) {
      this.statusDiv.textContent = status
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("[v0] Initializing AI Assistant...")
  new AIAssistant()
  console.log("[v0] AI Assistant initialized successfully")
})

window.addEventListener("error", (event) => {
  console.error("[v0] JavaScript error:", event.error)
})
