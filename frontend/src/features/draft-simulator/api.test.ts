import { afterEach, describe, expect, it, vi } from "vitest";
import {
  fetchBanRecommendations,
  fetchPickRecommendations,
} from "./api";
import type {
  RecommendationRequest,
  RecommendationResponse,
} from "./types/draft";

const payload: RecommendationRequest = {
  team: "blue",
  blue_picks: ["Akai"],
  red_picks: ["Claude"],
  blue_bans: ["Fanny"],
  red_bans: ["Joy"],
  top_k: 2,
  strict_turn: true,
  rerank_pool_size: null,
};

const responsePayload: RecommendationResponse = {
  team: "blue",
  recommendations: [
    {
      hero: "Akai",
      rank: 1,
      score: 9.1,
      reasons: ["mock reason"],
    },
  ],
  reasoning: "mock reasoning",
};

afterEach(() => {
  vi.unstubAllGlobals();
});

function mockFetch(response: Partial<Response>) {
  const fetchMock = vi.fn().mockResolvedValue(response as Response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("draft simulator API client", () => {
  it("posts ban recommendation requests to the hosted backend", async () => {
    const fetchMock = mockFetch({
      ok: true,
      json: vi.fn().mockResolvedValue(responsePayload),
    });

    await expect(fetchBanRecommendations(payload)).resolves.toEqual(
      responsePayload,
    );

    expect(fetchMock).toHaveBeenCalledWith(
      "https://ml-2-8lkf.onrender.com/draft/recommend-bans",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      },
    );
  });

  it("posts pick recommendation requests to the hosted backend", async () => {
    const fetchMock = mockFetch({
      ok: true,
      json: vi.fn().mockResolvedValue(responsePayload),
    });

    await fetchPickRecommendations(payload);

    expect(fetchMock).toHaveBeenCalledWith(
      "https://ml-2-8lkf.onrender.com/draft/recommend-picks",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(payload),
      }),
    );
  });

  it("throws a helpful error when the backend returns a non-OK response", async () => {
    mockFetch({
      ok: false,
      status: 503,
    });

    await expect(fetchBanRecommendations(payload)).rejects.toThrow(
      "Request failed: 503",
    );
  });
});
