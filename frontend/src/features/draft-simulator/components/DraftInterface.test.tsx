import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DraftInterface } from "./DraftInterface";

const recommendationResponse = {
  recommendation: {
    team: "blue",
    recommendations: [
      {
        hero: "Akai",
        rank: 1,
        score: 9.25,
        reasons: ["strong fit for this exact slot"],
      },
    ],
  },
  advisor: {
    uses_llm: false,
    provider: "local-semantic",
    model: "mock-advisor",
    advice: "Ban Akai.",
    retrieved_principles: [],
  },
};

beforeEach(() => {
  vi.spyOn(console, "log").mockImplementation(() => undefined);
  vi.spyOn(console, "error").mockImplementation(() => undefined);
});

afterEach(() => {
  vi.useRealTimers();
});

function mockRecommendationFetch() {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: vi.fn().mockResolvedValue(recommendationResponse),
  } as unknown as Response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function requestBodyAt(fetchMock: ReturnType<typeof vi.fn>, index: number) {
  const [, init] = fetchMock.mock.calls[index] as [string, RequestInit];
  return JSON.parse(String(init.body));
}

describe("DraftInterface", () => {
  it("renders the initial draft page without recommendations", () => {
    render(<DraftInterface />);

    expect(screen.getByRole("button", { name: /^start$/i })).toBeEnabled();
    expect(screen.getByRole("button", { name: /reset/i })).toBeEnabled();
    expect(screen.getByText("Ban")).toBeInTheDocument();
    expect(screen.getByText("30")).toBeInTheDocument();
    expect(screen.queryByText("Blue Suggestions")).not.toBeInTheDocument();
    expect(screen.queryByText("Red Suggestions")).not.toBeInTheDocument();
  });

  it("filters heroes by selected role", async () => {
    const user = userEvent.setup();
    render(<DraftInterface />);

    await user.click(screen.getByRole("button", { name: "Mage" }));

    expect(
      screen.queryByRole("button", { name: /miya/i }),
    ).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /eudora/i })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "All" }));

    expect(screen.getByRole("button", { name: /miya/i })).toBeInTheDocument();
  });

  it("starts the draft, fetches recommendations, and shows the active team panel", async () => {
    const fetchMock = mockRecommendationFetch();
    const user = userEvent.setup();
    render(<DraftInterface />);

    await user.click(screen.getByRole("button", { name: /^start$/i }));

    expect(screen.getByRole("button", { name: /^start$/i })).toBeDisabled();
    expect(await screen.findByText("Blue Suggestions")).toBeInTheDocument();
    expect(await screen.findByText("#1 Akai")).toBeInTheDocument();
    expect(screen.queryByText("Red Suggestions")).not.toBeInTheDocument();

    expect(fetchMock).toHaveBeenCalledWith(
      "https://ml-2-8lkf.onrender.com/draft/advise-bans",
      expect.objectContaining({
        method: "POST",
      }),
    );
    expect(requestBodyAt(fetchMock, 0)).toEqual({
      team: "blue",
      blue_picks: [],
      red_picks: [],
      blue_bans: [],
      red_bans: [],
      top_k: 3,
      strict_turn: true,
      rerank_pool_size: null,
    });
  });

  it("selects a hero into the current ban slot and sends the updated payload", async () => {
    const fetchMock = mockRecommendationFetch();
    const user = userEvent.setup();
    render(<DraftInterface />);

    await user.click(screen.getByRole("button", { name: /^start$/i }));
    await screen.findByText("#1 Akai");
    await user.click(screen.getByRole("button", { name: /miya/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));

    expect(screen.getAllByAltText("Miya")).toHaveLength(2);
    expect(await screen.findByText("Red Suggestions")).toBeInTheDocument();
    expect(requestBodyAt(fetchMock, 1)).toEqual({
      team: "red",
      blue_picks: [],
      red_picks: [],
      blue_bans: ["Miya"],
      red_bans: [],
      top_k: 3,
      strict_turn: true,
      rerank_pool_size: null,
    });
  });

  it("resets selections, timer, and recommendation panels", async () => {
    mockRecommendationFetch();
    const user = userEvent.setup();
    render(<DraftInterface />);

    await user.click(screen.getByRole("button", { name: /^start$/i }));
    await screen.findByText("#1 Akai");
    await user.click(screen.getByRole("button", { name: /miya/i }));
    expect(screen.getAllByAltText("Miya")).toHaveLength(2);

    await user.click(screen.getByRole("button", { name: /reset/i }));

    expect(screen.getByRole("button", { name: /^start$/i })).toBeEnabled();
    expect(screen.getByText("30")).toBeInTheDocument();
    expect(screen.queryByText("Blue Suggestions")).not.toBeInTheDocument();
    expect(screen.queryByText("Red Suggestions")).not.toBeInTheDocument();
    expect(screen.getAllByAltText("Miya")).toHaveLength(1);
  });

  it("counts down once the draft starts", async () => {
    vi.useFakeTimers();
    mockRecommendationFetch();
    render(<DraftInterface />);

    fireEvent.click(screen.getByRole("button", { name: /^start$/i }));

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(screen.getByText("29")).toBeInTheDocument();
  });
});
