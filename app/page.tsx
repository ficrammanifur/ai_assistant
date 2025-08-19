export default function Page() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">🤖 Raspberry Pi 5 AI Assistant</h1>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-yellow-800">
              <strong>Note:</strong> This is a Python Flask project designed to run on Raspberry Pi 5, not a Next.js web
              application. The files you need are Python-based.
            </p>
          </div>

          <div className="space-y-6">
            <section>
              <h2 className="text-2xl font-semibold text-gray-700 mb-3">📁 Project Files</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                <ul className="space-y-2 text-sm font-mono">
                  <li>
                    • <strong>app.py</strong> - Main Flask server
                  </li>
                  <li>
                    • <strong>oled_display.py</strong> - OLED display controller
                  </li>
                  <li>
                    • <strong>templates/index.html</strong> - Web interface
                  </li>
                  <li>
                    • <strong>static/style.css</strong> - Styling
                  </li>
                  <li>
                    • <strong>static/script.js</strong> - JavaScript functionality
                  </li>
                  <li>
                    • <strong>requirements.txt</strong> - Python dependencies
                  </li>
                  <li>
                    • <strong>setup.sh</strong> - Installation script
                  </li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-700 mb-3">🚀 How to Run on Raspberry Pi 5</h2>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
                <div className="space-y-2">
                  <div># 1. Download and extract the project files to your Raspberry Pi</div>
                  <div># 2. Make setup script executable and run it</div>
                  <div className="text-yellow-400">chmod +x setup.sh && ./setup.sh</div>
                  <div># 3. Activate the virtual environment</div>
                  <div className="text-yellow-400">source ai_assistant_env/bin/activate</div>
                  <div># 4. Start the AI Assistant</div>
                  <div className="text-yellow-400">python app.py</div>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-700 mb-3">🌐 Access Methods</h2>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-blue-800 mb-2">Web Interface</h3>
                  <p className="text-sm text-blue-600">
                    Open <code className="bg-blue-100 px-1 rounded">http://localhost:5000</code> in your browser
                  </p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-green-800 mb-2">Terminal Interface</h3>
                  <p className="text-sm text-green-600">Automatically starts when you run the Python script</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-purple-800 mb-2">OLED Display</h3>
                  <p className="text-sm text-purple-600">Shows AI expressions (if hardware connected)</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-700 mb-3">✨ Features</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Voice-to-text input via microphone
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Enter key to send messages
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    OLED facial expressions
                  </li>
                </ul>
                <ul className="space-y-2">
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Offline AI model (DistilGPT-2)
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Web and terminal interfaces
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    Network accessible
                  </li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-700 mb-3">🔧 Troubleshooting</h2>
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <p className="text-red-800 mb-2">
                  <strong>If Enter key and voice chat don't work:</strong>
                </p>
                <p className="text-sm text-red-600">
                  Make sure <code>static/script.js</code> exists and is accessible. Check the browser console for any
                  JavaScript errors.
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
