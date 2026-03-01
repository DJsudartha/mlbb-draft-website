import { User, ChevronRight, ChevronLeft } from "lucide-react";
import { Hero } from "../types/draft";

interface PickSectionProps {
  picks: Hero[];
  team: "blue" | "red";
  currentPickIndex?: number;
}

export function PickSection({
  picks,
  team,
  currentPickIndex,
}: PickSectionProps) {
  const emptySlots = Array(5 - picks.length).fill(null);
  const borderColor =
    team === "blue" ? "border-blue-500" : "border-red-500";
  const glowColor =
    team === "blue"
      ? "shadow-blue-500/50"
      : "shadow-red-500/50";
  const highlightColor =
    team === "blue"
      ? "border-blue-400 shadow-blue-400/70"
      : "border-red-400 shadow-red-400/70";
  const ArrowIcon =
    team === "blue" ? ChevronRight : ChevronLeft;

  return (
    <div>
      <h3 className="mb-3 text-sm text-gray-400">Picks</h3>
      <div className="space-y-2">
        {picks.map((hero, index) => (
          <div
            key={index}
            className={`relative rounded-lg border-2 ${borderColor} bg-black/40 overflow-hidden shadow-lg ${glowColor}`}
          >
            <div className="aspect-[4/3] w-full">
              <img
                src={hero.image}
                alt={hero.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent py-1 px-2">
              <div className="text-xs truncate">
                {hero.name}
              </div>
            </div>
          </div>
        ))}
        {emptySlots.map((_, index) => {
          const slotIndex = picks.length + index;
          const isActive = currentPickIndex === slotIndex;

          return (
            <div
              key={`empty-${index}`}
              className={`relative rounded-lg border-2 ${
                isActive
                  ? `${highlightColor} shadow-lg animate-pulse`
                  : `border-dashed ${borderColor} bg-black/30`
              } aspect-[4/3] flex items-center justify-center`}
            >
              {isActive && (
                <div
                  className={`absolute ${team === "blue" ? "left-0 -translate-x-8" : "right-0 translate-x-8"}`}
                >
                  <ArrowIcon
                    className="w-6 h-6 text-yellow-400 animate-pulse"
                    strokeWidth={3}
                  />
                </div>
              )}
              <User className="w-8 h-8 text-gray-600" />
            </div>
          );
        })}
      </div>
    </div>
  );
}