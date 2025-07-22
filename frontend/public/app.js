function App() {
  return (
    <div>
      <h1>Doctor Appointment Assistant</h1>
      <h2>Chat</h2>
      <Chat />
      <h2>Appointments</h2>
      <Calendar />
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
