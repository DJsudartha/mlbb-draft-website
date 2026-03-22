export type Role =
  | "Tank"
  | "Fighter"
  | "Assassin"
  | "Mage"
  | "Marksman"
  | "Support"
  | "Other";

export type DraftPhase = "ban1" | "pick1" | "ban2" | "pick2";

export type DraftAction = "ban" | "pick";

export type Team = "blue" | "red";

export interface Hero {
  id: number;
  name: string;
  role: Role[];     
  image: string;
}

export interface DraftStep {
  phase: DraftPhase;
  team: Team;
  action: DraftAction;
}