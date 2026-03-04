import { useState, useEffect } from "react";
import { HeroGrid } from "./HeroGrid";
import type { Hero, DraftPhase } from "../types/draft.ts";
import { heroes } from "../data/heroes";
import { X, ChevronRight, ChevronLeft } from "lucide-react";

const draftOrder: {
    phase: DraftPhase;
    team: "blue" | "red";
    action: "ban" | "pick";
  }[] = [
    // First ban phase (5 bans each)
    { phase: "ban1", team: "blue", action: "ban" },
    { phase: "ban1", team: "red", action: "ban" },
    { phase: "ban1", team: "blue", action: "ban" },
    { phase: "ban1", team: "red", action: "ban" },
    { phase: "ban1", team: "blue", action: "ban" },
    { phase: "ban1", team: "red", action: "ban" },

    // First pick phase
    { phase: "pick1", team: "blue", action: "pick" },
    { phase: "pick1", team: "red", action: "pick" },
    { phase: "pick1", team: "red", action: "pick" },
    { phase: "pick1", team: "blue", action: "pick" },
    { phase: "pick1", team: "blue", action: "pick" },
    { phase: "pick1", team: "red", action: "pick" },

    // Second ban phase
    { phase: "ban1", team: "red", action: "ban" },
    { phase: "ban1", team: "blue", action: "ban" },
    { phase: "ban1", team: "red", action: "ban" },
    { phase: "ban1", team: "blue", action: "ban" },

    // Final pick phase
    { phase: "pick1", team: "red", action: "pick" },
    { phase: "pick1", team: "blue", action: "pick" },
    { phase: "pick1", team: "blue", action: "pick" },
    { phase: "pick1", team: "red", action: "pick" },
  ];

export function DraftInterface() {
  const [timeRemaining, setTimeRemaining] = useState(30);

  const [blueBans, setBlueBans] = useState<Hero[]>([]);
  const [redBans, setRedBans] = useState<Hero[]>([]);
  const [bluePicks, setBluePicks] = useState<Hero[]>([]);
  const [redPicks, setRedPicks] = useState<Hero[]>([]);

  const [bannedHeroIds, setBannedHeroIds] = useState<
    Set<number>
  >(new Set());
  const [pickedHeroIds, setPickedHeroIds] = useState<
    Set<number>
  >(new Set());

  const [currentDraftIndex, setCurrentDraftIndex] = useState(0);
  const currentStep =
    currentDraftIndex < draftOrder.length
      ? draftOrder[currentDraftIndex]
      : null;
  const currentTeam = currentStep ? currentStep.team : null;
  const currentAction = currentStep ? currentStep.action : "complete";

  useEffect(() => {
    if (currentDraftIndex >= draftOrder.length) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          setCurrentDraftIndex((i) => i + 1);
          return 30;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [currentDraftIndex]);

  const handleHeroSelect = (hero: Hero) => {
    if (currentDraftIndex >= draftOrder.length) return;
    if (
      bannedHeroIds.has(hero.id) ||
      pickedHeroIds.has(hero.id)
    )
      return;

    const current = draftOrder[currentDraftIndex];

    if (current.action === "ban") {
      if (current.team === "blue" && blueBans.length < 5) {
        setBlueBans([...blueBans, hero]);
        setBannedHeroIds(new Set([...bannedHeroIds, hero.id]));
        setCurrentDraftIndex((i) => i + 1);
      } else if (current.team === "red" && redBans.length < 5) {
        setRedBans([...redBans, hero]);
        setBannedHeroIds(new Set([...bannedHeroIds, hero.id]));
        setCurrentDraftIndex((i) => i + 1);
      }
    } else if (current.action === "pick") {
      if (current.team === "blue" && bluePicks.length < 5) {
        setBluePicks([...bluePicks, hero]);
        setPickedHeroIds(new Set([...pickedHeroIds, hero.id]));
        setCurrentDraftIndex((i) => i + 1);
      } else if (
        current.team === "red" &&
        redPicks.length < 5
      ) {
        setRedPicks([...redPicks, hero]);
        setPickedHeroIds(new Set([...pickedHeroIds, hero.id]));
        setCurrentDraftIndex((i) => i + 1);
      }
    }
  };

  // Center label (Ban / Pick / Complete)
  const centerLabel =
    currentAction === "ban"
      ? "Ban"
      : currentAction === "pick"
        ? "Pick"
        : "Complete";

  // Calculate current slot index for highlighting (global 0..9 for bans: 0..4 blue, 5..9 red)
  const getCurrentBanIndex = () => {
    if (
      currentDraftIndex >= draftOrder.length ||
      currentAction !== "ban"
    )
      return -1;
    const current = draftOrder[currentDraftIndex];
    return current.team === "blue"
      ? blueBans.length
      : 5 + redBans.length;
  };

  const currentBanIndex = getCurrentBanIndex();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white flex flex-col">
      {/* TOP BAR: Blue Bans | Center Timer | Red Bans */}
      <div className="container mx-auto px-4 pt-3">
        <div className="bg-black/50 backdrop-blur-sm border border-white/10 rounded-xl px-4 py-2 flex items-center justify-between">
          <div className="w-[320px] flex justify-start">
            <div className="flex gap-2">
              {[...Array(5)].map((_, index) => {
                const hero = blueBans[index];
                const isActive = currentBanIndex === index;

                return (
                  <div
                    key={`top-blue-ban-${index}`}
                    className={`relative w-12 h-12 rounded-full overflow-hidden flex items-center justify-center
                      ${hero ? "border border-gray-700 bg-gray-800" : "border border-dashed border-gray-600 bg-gray-900/40"}
                      ${isActive ? "ring-2 ring-blue-400 animate-pulse" : ""}
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
                          <X
                            className="w-4 h-4 text-red-500"
                            strokeWidth={3}
                          />
                        </div>
                      </>
                    ) : (
                      <span className="text-gray-500 text-xs">
                        ?
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* CENTER: BAN/PICK + TIMER */}
          {/* CENTER: BAN/PICK + TIMER + ARROW */}
          <div className="flex flex-col items-center justify-center">
            <div className="text-xl font-bold leading-none">
              {centerLabel}
            </div>

            {currentAction === "complete" ? (
              <div className="text-green-400 text-sm font-semibold mt-1">
                Complete
              </div>
            ) : (
              <div className="flex items-center gap-2 mt-1">
                {/* Left arrow slot (fixed width, doesn’t move layout) */}
                <div className="w-5 h-5 flex items-center justify-center">
                  <ChevronLeft
                    className={`w-5 h-5 ${
                      currentTeam === "blue"
                        ? "text-blue-400 drop-shadow-[0_0_6px_currentColor]"
                        : "opacity-0"
                    }`}
                  />
                </div>

                {/* Timer (fixed width, centered) */}
                <div className="text-sm font-semibold tabular-nums w-[3ch] text-center">
                  {timeRemaining}
                </div>

                {/* Right arrow slot (fixed width, doesn’t move layout) */}
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

          {/* RIGHT: RED BANS */}
          <div className="w-[320px] flex justify-end">
            <div className="flex gap-2">
              {[...Array(5)].map((_, index) => {
                const hero = redBans[index];
                const isActive = currentBanIndex === 5 + index;

                return (
                  <div
                    key={`top-red-ban-${index}`}
                    className={`relative w-12 h-12 rounded-full overflow-hidden flex items-center justify-center
                      ${hero ? "border border-gray-700 bg-gray-800" : "border border-dashed border-gray-600 bg-gray-900/40"}
                      ${isActive ? "ring-2 ring-red-400 animate-pulse" : ""}
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
                          <X
                            className="w-4 h-4 text-red-500"
                            strokeWidth={3}
                          />
                        </div>
                      </>
                    ) : (
                      <span className="text-gray-500 text-xs">
                        ?
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 container mx-auto px-4 py-4 grid grid-cols-[180px_1fr_180px] gap-4">
        {/* Blue Team Picks */}
        <div className="space-y-2">
          {[...Array(5)].map((_, index) => {
            const hero = bluePicks[index];
            const isActive =
              currentAction === "pick" &&
              currentTeam === "blue" &&
              bluePicks.length === index;

            return (
              <div
                key={`blue-pick-${index}`}
                className={`relative rounded-lg overflow-hidden ${
                  isActive
                    ? "ring-2 ring-blue-400 ring-offset-1 ring-offset-gray-900 animate-pulse"
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
                    <span className="text-gray-600 text-2xl">
                      ?
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Hero Grid */}
        <div>
          <HeroGrid
            heroes={heroes}
            onHeroSelect={handleHeroSelect}
            bannedHeroIds={bannedHeroIds}
            pickedHeroIds={pickedHeroIds}
            currentAction={currentAction}
          />
        </div>

        {/* Red Team Picks */}
        <div className="space-y-2">
          {[...Array(5)].map((_, index) => {
            const hero = redPicks[index];
            const isActive =
              currentAction === "pick" &&
              currentTeam === "red" &&
              redPicks.length === index;

            return (
              <div
                key={`red-pick-${index}`}
                className={`relative rounded-lg overflow-hidden ${
                  isActive
                    ? "ring-2 ring-red-400 ring-offset-1 ring-offset-gray-900 animate-pulse"
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
                    <span className="text-gray-600 text-2xl">
                      ?
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}