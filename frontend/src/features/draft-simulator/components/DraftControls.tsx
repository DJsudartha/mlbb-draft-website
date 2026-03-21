import { RotateCcw } from "lucide-react";

type Props = {
  hasDraftStarted: boolean;
  onStart: () => void;
  onReset: () => void;
};

export function DraftControls({
  hasDraftStarted,
  onStart,
  onReset,
}: Props) {
  return (
    <div className="w-[320px] flex justify-end items-center gap-3 pr-6">
      <button
        type="button"
        onClick={onStart}
        disabled={hasDraftStarted}
        className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm border
          ${
            hasDraftStarted
              ? "bg-gray-700 border-gray-600 text-gray-400 cursor-not-allowed"
              : "bg-green-600 border-green-500 text-white hover:bg-green-500"
          }
        `}
      >
        Start
      </button>

      <button
        type="button"
        onClick={onReset}
        className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-200 hover:bg-white/10"
      >
        <RotateCcw className="w-4 h-4" />
        Reset
      </button>
    </div>
  );
}