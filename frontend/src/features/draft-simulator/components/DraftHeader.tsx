import { ChevronLeft, ChevronRight } from "lucide-react";

type Props = {
  currentAction: "ban" | "pick" | "complete";
  currentTeam: "blue" | "red" | null;
  timeRemaining: number;
  hasDraftStarted: boolean;
};

export function DraftHeader({
  currentAction,
  currentTeam,
  timeRemaining,
  hasDraftStarted,
}: Props) {
  const centerLabel =
    currentAction === "ban"
      ? "Ban"
      : currentAction === "pick"
        ? "Pick"
        : "Complete";

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="text-xl font-bold leading-none">{centerLabel}</div>

      {currentAction === "complete" ? (
        <div className="text-green-400 text-sm font-semibold mt-1">
          Complete
        </div>
      ) : !hasDraftStarted ? (
        <div className="text-sm font-semibold mt-1 text-gray-300">30</div>
      ) : (
        <div className="flex items-center gap-2 mt-1">
          <div className="w-5 h-5 flex items-center justify-center">
            <ChevronLeft
              className={`w-5 h-5 ${
                currentTeam === "blue"
                  ? "text-blue-400 drop-shadow-[0_0_6px_currentColor]"
                  : "opacity-0"
              }`}
            />
          </div>

          <div className="text-sm font-semibold tabular-nums w-[3ch] text-center">
            {timeRemaining}
          </div>

          <div className="w-5 h-5 flex items-center justify-center">
            <ChevronRight
              className={`w-5 h-5 ${
                currentTeam === "red"
                  ? "text-red-400 drop-shadow-[0_0_6px_currentColor]"
                  : "opacity-0"
              }`}
            />
          </div>
        </div>
      )}
    </div>
  );
}