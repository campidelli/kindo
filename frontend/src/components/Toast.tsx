interface Props {
  message: string | null;
  type: "error" | "warning";
  onDismiss: () => void;
}

export default function Toast({ message, type, onDismiss }: Props) {
  if (!message) return null;

  const styles =
    type === "error"
      ? "bg-red-50 border-red-300 text-red-800"
      : "bg-amber-50 border-amber-300 text-amber-800";

  return (
    <div className={`fixed top-5 right-5 z-50 flex max-w-sm items-start gap-3 rounded-lg border px-4 py-3 shadow-lg ${styles}`}>
      <p className="flex-1 text-sm">{message}</p>
      <button
        onClick={onDismiss}
        aria-label="Dismiss"
        className="shrink-0 text-lg leading-none opacity-60 hover:opacity-100"
      >
        ×
      </button>
    </div>
  );
}
