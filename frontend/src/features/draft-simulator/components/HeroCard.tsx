import { X, Check } from "lucide-react";
import type { Hero } from "../types/draft";

interface HeroCardProps {
  hero: Hero;
  onClick: () => void;
  isBanned: boolean;
  isPicked: boolean;
  disabled: boolean;
}

export function HeroCard({
  hero,
  onClick,
  isBanned,
  isPicked,
  disabled,
}: HeroCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`relative flex flex-col items-center gap-1 transition-all group ${
        disabled
          ? "cursor-not-allowed"
          : "hover:scale-110 cursor-pointer"
      }`}
    >
      <div
        className={`relative w-14 h-14 rounded-full overflow-hidden border-2 transition-all ${
          disabled
            ? "border-gray-700"
            : "border-purple-500/50 hover:border-yellow-400 hover:shadow-lg hover:shadow-yellow-400/50"
        }`}
      >
        <img
          src={hero.image}
          alt={hero.name}
          className={`w-full h-full object-cover ${
            isBanned || isPicked ? "opacity-30 grayscale" : ""
          }`}
        />

        {/* Banned/Picked Overlay */}
        {isBanned && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/60">
            <X
              className="w-6 h-6 text-red-500"
              strokeWidth={3}
            />
          </div>
        )}
        {isPicked && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/60">
            <Check
              className="w-6 h-6 text-green-500"
              strokeWidth={3}
            />
          </div>
        )}
      </div>

      {/* Hero Name */}
      <div className="text-[10px] text-center truncate w-20 px-1">
        {hero.name}
      </div>
    </button>
  );
}