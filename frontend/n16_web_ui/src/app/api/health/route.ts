import { env } from "@/lib/env";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function GET() {
  const maxRetries = 30;
  const retryDelayMs = 1000;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(`${env.BACKEND_URL}/health`, {
        method: "GET",
        headers: { "X-Internal-Key": env.INTERNAL_API_KEY },
        cache: "no-store",
      });
      if (!res.ok) {
        if (attempt < maxRetries) {
          await sleep(retryDelayMs);
          continue;
        }
        return Response.json({ status: "error" }, { status: res.status });
      }
      const data = await res.json();
      return Response.json(data);
    } catch (err) {
      if (attempt < maxRetries) {
        await sleep(retryDelayMs);
        continue;
      }
      return Response.json(
        { status: "error", message: err instanceof Error ? err.message : "Failed to fetch health" },
        { status: 502 },
      );
    }
  }
}
