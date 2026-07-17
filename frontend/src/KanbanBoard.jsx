import { useCallback, useEffect, useState } from "react";
import { fetchApplications, updateApplicationStatus } from "./api.js";
import Column from "./Column.jsx";

export default function KanbanBoard() {
  const [applications, setApplications] = useState([]);

  const refresh = useCallback(async () => {
    setApplications(await fetchApplications());
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleDrop = async (id, status) => {
    await updateApplicationStatus(id, status);
    await refresh();
  };

  const columns = groupByStatus(applications);

  return (
    <div className="board">
      {[...columns.entries()].map(([status, apps]) => (
        <Column key={status} status={status} applications={apps} onDrop={handleDrop} />
      ))}
    </div>
  );
}

function groupByStatus(applications) {
  const groups = new Map();
  for (const application of applications) {
    if (!groups.has(application.status)) groups.set(application.status, []);
    groups.get(application.status).push(application);
  }
  return groups;
}
