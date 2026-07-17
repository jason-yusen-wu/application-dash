import { useState } from "react";
import Card from "./Card.jsx";

export default function Column({ status, applications, onDrop }) {
  const [isOver, setIsOver] = useState(false);

  return (
    <div
      className={`column${isOver ? " drag-over" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setIsOver(true);
      }}
      onDragLeave={() => setIsOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsOver(false);
        const id = Number(e.dataTransfer.getData("text/plain"));
        onDrop(id, status);
      }}
    >
      <h2>{status}</h2>
      {applications.map((application) => (
        <Card key={application.id} application={application} />
      ))}
    </div>
  );
}
