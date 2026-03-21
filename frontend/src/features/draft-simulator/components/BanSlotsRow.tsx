import { X } from "lucide-react";
import type { Hero } from "../types/draft";

type Props = {
  heroes: Hero[];
  activeIndex: number;
  side: "blue" | "red";
  align: "left" | "right";
};

export function BanSlotsRow({ heroes, activeIndex, side, align }: Props) {
  return (
    <div
      className={`w-[320px] flex ${
        align === "left" ? "justify-start" : "justify-end"
      }`}
    >
      <div className="flex gap-2">
        {[...Array(5)].map((_, index) => {
          const hero = heroes[index];
          const isActive = activeIndex === index;

          return (
            <div
              key={`${side}-ban-${index}`}
              className={`relative w-12 h-12 rounded-full overflow-hidden flex items-center justify-center
                ${
                  hero
                    ? "border border-gray-700 bg-gray-800"
                    : "border border-dashed border-gray-600 bg-gray-900/40"
                }
                ${
                  isActive
                    ? side === "blue"
                      ? "ring-2 ring-blue-400 animate-pulse"
                      : "ring-2 ring-red-400 animate-pulse"
                    : ""
                }
              `}
            >
              {hero ? (
                <>
                  <img
                    src={hero.image}
                    alt={hero.name}
                    className="w-full h-full object-cover opacity-40"
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <X className="w-4 h-4 text-red-500" strokeWidth={3} />
                  </div>
                </>
              ) : (
                <span className="text-gray-500 text-xs">?</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}