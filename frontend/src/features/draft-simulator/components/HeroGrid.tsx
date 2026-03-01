import { useState } from "react";
import { Hero, Role } from "../types/draft";
import { HeroCard } from "./HeroCard";

interface HeroGridProps {
  heroes: Hero[];
  onHeroSelect: (hero: Hero) => void;
  bannedHeroIds: Set<number>;
  pickedHeroIds: Set<number>;
  currentAction: string;
}

const roles: Array<"All" | Role> = [
  "All",
  "Tank",
  "Fighter",
  "Assassin",
  "Mage",
  "Marksman",
  "Support",
];

export function HeroGrid({
  heroes,
  onHeroSelect,
  bannedHeroIds,
  pickedHeroIds,
  currentAction,
}: HeroGridProps) {
  const [selectedRole, setSelectedRole] = useState<"All" | Role>("All");

  const filteredHeroes =
    selectedRole === "All"
      ? heroes
      : heroes.filter((hero) => hero.role.includes(selectedRole));

  return (
    <div className="bg-gray-900/80 backdrop-blur-sm rounded-lg border border-gray-700/50 p-4 h-full flex flex-col">
      {/* Role Filter */}
      <div className="mb-4 grid grid-cols-7 gap-2 bg-gray-800/50 rounded-lg p-2">
        {roles.map((role) => (
          <button
            key={role}
            onClick={() => setSelectedRole(role)}
            className={`px-2 py-2 rounded-lg transition-all text-sm text-center ${
              selectedRole === role
                ? "bg-purple-600 text-white shadow-lg shadow-purple-500/30"
                : "bg-gray-700/50 text-gray-300 hover:bg-gray-600/50"
            }`}
          >
            {role}
          </button>
        ))}
      </div>

      {/* Heroes Grid */}
      <div className="grid grid-cols-8 gap-4 overflow-y-auto pr-2 custom-scrollbar">
        {filteredHeroes.map((hero) => (
          <HeroCard
            key={hero.id}
            hero={hero}
            onClick={() => onHeroSelect(hero)}
            isBanned={bannedHeroIds.has(hero.id)}
            isPicked={pickedHeroIds.has(hero.id)}
            disabled={
              bannedHeroIds.has(hero.id) ||
              pickedHeroIds.has(hero.id) ||
              currentAction === "complete"
            }
          />
        ))}
      </div>
    </div>
  );
}