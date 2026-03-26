import type { DraftPhase } from "../types/draft";

export const draftOrder: {
    phase: DraftPhase;
    team: "blue" | "red";
    action: "ban" | "pick";
    count: number;
  }[] = [
    // First ban phase (5 bans each)
    { phase: "ban1", team: "blue", action: "ban" , count: 1},
    { phase: "ban1", team: "red", action: "ban" , count: 1},
    { phase: "ban1", team: "blue", action: "ban" , count: 1},
    { phase: "ban1", team: "red", action: "ban" , count: 1},
    { phase: "ban1", team: "blue", action: "ban" , count: 1},
    { phase: "ban1", team: "red", action: "ban" , count: 1},

    // First pick phase
    { phase: "pick1", team: "blue", action: "pick", count: 1},
    { phase: "pick1", team: "red", action: "pick", count: 2},
    { phase: "pick1", team: "blue", action: "pick", count: 2},
    { phase: "pick1", team: "red", action: "pick", count: 1},

    // Second ban phase
    { phase: "ban2", team: "red", action: "ban", count: 1},
    { phase: "ban2", team: "blue", action: "ban", count: 1},
    { phase: "ban2", team: "red", action: "ban", count: 1},
    { phase: "ban2", team: "blue", action: "ban", count: 1},

    // Final pick phase
    { phase: "pick2", team: "red", action: "pick", count: 1},
    { phase: "pick2", team: "blue", action: "pick", count: 2},
    { phase: "pick2", team: "red", action: "pick", count: 1},
  ];