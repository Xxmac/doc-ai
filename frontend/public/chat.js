function Chat() {
  const [messages, setMessages] = React.useState([]);
  const [input, setInput] = React.useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { sender: "user", text: input };
    setMessages(prev => [...prev, userMessage]);
    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input })
      });
      const data = await res.json();
      const botMessage = { sender: "bot", text: data.response };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      const botMessage = { sender: "bot", text: "Error: " + err.message };
      setMessages(prev => [...prev, botMessage]);
    }
    setInput("");
  };

  return (
    <div>
      <div className="chat-container">
        {messages.map((m, idx) => (
          <div key={idx}><strong>{m.sender}:</strong> {m.text}</div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter') sendMessage(); }}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
