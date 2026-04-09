interface Props {
  isOpen: boolean;
}

export default function ProcessingModal({ isOpen }: Props) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="flex flex-col items-center gap-4 rounded-xl bg-white p-8 shadow-xl">
        <div className="size-10 animate-spin rounded-full border-4 border-green-200 border-t-green-600" />
        <p className="text-sm font-medium text-gray-700">Processing payment…</p>
      </div>
    </div>
  );
}
