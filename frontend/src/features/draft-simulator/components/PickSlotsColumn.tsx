import type { Hero } from "../types/draft";

type Props = {
  heroes: Hero[];
  currentAction: "ban" | "pick" | "complete";
  currentTeam: "blue" | "red" | null;
  side: "blue" | "red";
};

export function PickSlotsColumn({
  heroes,
  currentAction,
  currentTeam,
  side,
}: Props) {
  return (
    <div className="space-y-2">
      {[...Array(5)].map((_, index) => {
        const hero = heroes[index];
        const isActive =
          currentAction === "pick" &&
          currentTeam === side &&
          heroes.length === index;

        return (
          <div
            key={`${side}-pick-${index}`}
            className={`relative rounded-lg overflow-hidden ${
              isActive
                ? side === "blue"
                  ? "ring-2 ring-blue-400 ring-offset-1 ring-offset-gray-900 animate-pulse"
                  : "ring-2 ring-red-400 ring-offset-1 ring-offset-gray-900 animate-pulse"
                : "border border-gray-700"
            } bg-gray-800 h-24`}
          >
            {hero ? (
              <>
                <img
                  src={hero.image}
                  alt={hero.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-1">
                  <div className="text-[10px] text-center truncate">
                    {hero.name}
                  </div>
                </div>
              </>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <span className="text-gray-600 text-2xl">?</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}