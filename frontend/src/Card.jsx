export default function Card({ application }) {
  return (
    <div
      className="card"
      draggable
      onDragStart={(e) => e.dataTransfer.setData("text/plain", String(application.id))}
    >
      <strong>{application.company}</strong>
      <div>{application.role}</div>
    </div>
  );
}
